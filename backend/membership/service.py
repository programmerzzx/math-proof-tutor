"""
会员服务模块 - 核心业务逻辑
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import uuid

from .membership_models import (
    User, Order, Coupon,
    PRODUCT_PRICES, MEMBERSHIP_BENEFITS
)
from .benefits import BenefitsManager, problem_bank_service
from .payment import PaymentService, PaymentError


class MembershipError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class UserMembershipService:
    """用户会员服务"""
    
    def __init__(self, payment_service: PaymentService = None):
        self.payment_service = payment_service
        self._users: Dict[str, User] = {}
        self._orders: Dict[str, Order] = {}
        self._coupons: Dict[str, Coupon] = {}
    
    # ========== 用户管理 ==========
    
    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)
    
    def create_user(self, user_id: str, username: str, email: str) -> User:
        user = User(
            id=user_id,
            username=username,
            email=email,
            level="free",
            created_at=datetime.now()
        )
        self._users[user_id] = user
        return user
    
    def update_user_level(self, user_id: str, new_level: str, expires_at: Optional[datetime] = None) -> User:
        user = self.get_user(user_id)
        if not user:
            raise MembershipError("USER_NOT_FOUND", f"用户不存在: {user_id}")
        
        user.level = new_level
        
        if new_level != "lifetime":
            if expires_at:
                user.level_expires = expires_at
            else:
                user.level_expires = BenefitsManager.calculate_expire_date(new_level)
        
        user.updated_at = datetime.now()
        return user
    
    def get_user_membership_status(self, user_id: str) -> Dict[str, Any]:
        user = self.get_user(user_id)
        if not user:
            raise MembershipError("USER_NOT_FOUND", f"用户不存在: {user_id}")
        
        current_level = user.get_current_level()
        benefits = user.get_benefits()
        
        return {
            "user_id": user.id,
            "level": user.level,
            "effective_level": current_level,
            "is_active": user.is_membership_active(),
            "expires_at": user.level_expires.isoformat() if user.level_expires else None,
            "days_remaining": self._calculate_days_remaining(user),
            "benefits": self._format_benefits_summary(benefits),
            "ocr_stats": self._get_ocr_stats(user),
            "pricing_cards": BenefitsManager.get_pricing_cards(),
            "upgrade_path": BenefitsManager.get_upgrade_path(current_level)
        }
    
    def _calculate_days_remaining(self, user: User) -> Optional[int]:
        if user.level in ["free", "lifetime"]:
            return None
        if not user.level_expires:
            return 0
        delta = user.level_expires - datetime.now()
        return max(0, delta.days)
    
    def _format_benefits_summary(self, benefits: Dict) -> Dict:
        return {
            "problems_limit": benefits.get("problems_limit", 100),
            "ocr_daily_limit": benefits.get("ocr_daily_limit", 5),
            "analysis_depth": benefits.get("analysis_depth", "basic"),
            "can_expand_problems": benefits.get("expansion_access", False),
            "has_api_access": benefits.get("api_access", False)
        }
    
    def _get_ocr_stats(self, user: User) -> Dict:
        user._reset_daily_ocr_if_needed()
        remaining = user.get_remaining_ocr()
        
        return {
            "used_today": user.ocr_count_today,
            "remaining": remaining,
            "is_unlimited": remaining == -1
        }
    
    # ========== 订单管理 ==========
    
    def create_order(self, user_id: str, product: str, payment_method: str, coupon_code: Optional[str] = None) -> Dict:
        """创建订单"""
        if product not in PRODUCT_PRICES:
            raise MembershipError("INVALID_PRODUCT", f"无效的产品: {product}")
        
        if payment_method not in ["alipay", "wechat", "stripe"]:
            raise MembershipError("INVALID_PAYMENT", f"无效的支付方式: {payment_method}")
        
        amount = PRODUCT_PRICES[product]
        discount_amount = 0.0
        final_amount = amount
        
        # 应用优惠券
        if coupon_code:
            coupon = self._coupons.get(coupon_code)
            if coupon and coupon.is_valid():
                if coupon.discount_type == "percentage":
                    discount_amount = amount * (coupon.discount_value / 100)
                else:
                    discount_amount = coupon.discount_value
                final_amount = amount - discount_amount
                coupon.current_uses += 1
        
        # 创建订单
        order = Order(
            order_id=Order.generate_order_id(),
            user_id=user_id,
            product=product,
            amount=amount,
            payment_method=payment_method,
            discount_amount=discount_amount,
            final_amount=final_amount,
            coupon_code=coupon_code,
            status="pending"
        )
        
        self._orders[order.order_id] = order
        
        # 生成支付链接
        order_data = {
            "order_id": order.order_id,
            "amount": final_amount,
            "subject": f"数学证明导师-{BenefitsManager.get_level_display_name(product)}",
            "description": f"购买{product}会员服务"
        }
        
        payment_result = self.payment_service.create_payment(order_data, payment_method)
        
        return {
            "order_id": order.order_id,
            "amount": amount,
            "discount_amount": discount_amount,
            "final_amount": final_amount,
            "pay_url": payment_result.get("pay_url", ""),
            "qr_code_url": payment_result.get("qr_code_url", ""),
            "checkout_url": payment_result.get("checkout_url", ""),
            "expired_at": payment_result.get("expired_at"),
            "status": "pending"
        }
    
    def handle_payment_callback(self, payment_method: str, callback_data: Dict) -> Dict:
        """处理支付回调"""
        is_valid, data = self.payment_service.handle_callback(payment_method, callback_data)
        
        order_id = data.get("order_id")
        order = self._orders.get(order_id)
        
        if not order:
            raise MembershipError("ORDER_NOT_FOUND", f"订单不存在: {order_id}")
        
        if is_valid:
            order.status = "paid"
            order.paid_at = datetime.now()
            order.transaction_id = data.get("transaction_id")
            
            expires_at = BenefitsManager.calculate_expire_date(order.product)
            self.update_user_level(order.user_id, order.product, expires_at)
            
            return {
                "success": True,
                "order_id": order_id,
                "new_level": order.product,
                "message": "支付成功，会员已升级"
            }
        else:
            order.status = "failed"
            return {
                "success": False,
                "order_id": order_id,
                "message": data.get("error", "支付失败")
            }
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        order = self._orders.get(order_id)
        if not order:
            return None
        
        return {
            "order_id": order.order_id,
            "user_id": order.user_id,
            "product": order.product,
            "product_name": BenefitsManager.get_level_display_name(order.product),
            "amount": order.amount,
            "discount_amount": order.discount_amount,
            "final_amount": order.final_amount,
            "payment_method": order.payment_method,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "paid_at": order.paid_at.isoformat() if order.paid_at else None
        }
    
    def get_user_orders(self, user_id: str) -> List[Dict]:
        orders = [order for order in self._orders.values() if order.user_id == user_id]
        return [self.get_order(o.order_id) for o in orders]
    
    # ========== 优惠券 ==========
    
    def create_coupon(self, code: str, discount_type: str, discount_value: float, 
                      min_purchase: float = None, max_uses: int = -1, valid_days: int = None) -> Coupon:
        valid_from = datetime.now()
        valid_until = (valid_from + timedelta(days=valid_days)) if valid_days else None
        
        coupon = Coupon(
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            min_purchase=min_purchase,
            max_uses=max_uses,
            valid_from=valid_from,
            valid_until=valid_until
        )
        
        self._coupons[code] = coupon
        return coupon
    
    def validate_coupon(self, code: str, product: str, amount: float) -> Tuple[bool, Dict]:
        coupon = self._coupons.get(code)
        
        if not coupon:
            return False, {"error": "优惠券不存在"}
        
        if not coupon.is_valid():
            return False, {"error": "优惠券已过期或已达使用上限"}
        
        discount = 0
        if coupon.discount_type == "percentage":
            discount = amount * (coupon.discount_value / 100)
        else:
            discount = coupon.discount_value
        
        return True, {
            "code": code,
            "discount_amount": discount,
            "original_amount": amount,
            "final_amount": amount - discount
        }
    
    # ========== 题库扩充 ==========
    
    def expand_problems(self, user_id: str) -> Dict[str, Any]:
        user = self.get_user(user_id)
        if not user:
            raise MembershipError("USER_NOT_FOUND", "用户不存在")
        
        return problem_bank_service.expand_problem_bank(user.level)
    
    # ========== 退款 ==========
    
    def request_refund(self, order_id: str, reason: str = None) -> Dict:
        order = self._orders.get(order_id)
        
        if not order:
            raise MembershipError("ORDER_NOT_FOUND", "订单不存在")
        
        if order.status != "paid":
            raise MembershipError("INVALID_STATUS", "只能退款已支付的订单")
        
        if order.paid_at:
            days_elapsed = (datetime.now() - order.paid_at).days
            if days_elapsed > 7:
                raise MembershipError("REFUND_EXPIRED", "已超过7天退款期限")
        
        order.status = "refunded"
        
        user = self.get_user(order.user_id)
        if user and user.level == order.product:
            user.level = "free"
            user.level_expires = None
        
        return {
            "success": True,
            "refund_amount": order.final_amount,
            "message": "退款申请已提交"
        }


# 创建服务实例
def create_membership_service(gateway_config: Dict = None) -> UserMembershipService:
    payment_service = PaymentService(gateway_config) if gateway_config else PaymentService()
    return UserMembershipService(payment_service)
