"""
支付服务模块
"""
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import hashlib
import json
import base64


class PaymentError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class BasePaymentGateway:
    """支付网关基类"""
    
    def create_order(self, order_data: Dict) -> Dict:
        pass
    
    def verify_callback(self, callback_data: Dict) -> Tuple[bool, Dict]:
        pass


class AlipayGateway(BasePaymentGateway):
    """支付宝支付网关"""
    
    def __init__(self, config: Dict):
        self.app_id = config.get('app_id', '')
        self.private_key = config.get('private_key', '')
        self.alipay_public_key = config.get('alipay_public_key', '')
    
    def create_order(self, order_data: Dict) -> Dict:
        """创建支付宝订单"""
        biz_content = {
            "out_trade_no": order_data["order_id"],
            "total_amount": str(order_data["amount"]),
            "subject": order_data.get("subject", "会员订购"),
            "product_code": "FAST_INSTANT_TRADE_PAY",
            "timeout_express": "30m"
        }
        
        # 生成支付链接
        pay_url = f"https://qr.alipay.com/{order_data['order_id']}"
        
        return {
            "order_id": order_data["order_id"],
            "pay_url": pay_url,
            "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={pay_url}",
            "amount": order_data["amount"],
            "expired_at": (datetime.now() + timedelta(minutes=30)).isoformat()
        }
    
    def verify_callback(self, callback_data: Dict) -> Tuple[bool, Dict]:
        trade_status = callback_data.get('trade_status', '')
        is_success = trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']
        
        return is_success, {
            "order_id": callback_data.get('out_trade_no'),
            "transaction_id": callback_data.get('trade_no'),
            "amount": float(callback_data.get('total_amount', 0)),
            "status": "success" if is_success else "failed"
        }


class WechatPayGateway(BasePaymentGateway):
    """微信支付网关"""
    
    def __init__(self, config: Dict):
        self.app_id = config.get('app_id', '')
        self.mch_id = config.get('mch_id', '')
        self.api_key = config.get('api_key', '')
    
    def create_order(self, order_data: Dict) -> Dict:
        """创建微信支付订单"""
        total_fee = int(order_data["amount"] * 100)
        
        code_url = f"weixin://wxpay/bizpayurl?pr={order_data['order_id']}"
        
        return {
            "order_id": order_data["order_id"],
            "code_url": code_url,
            "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={code_url}",
            "amount": order_data["amount"],
            "expired_at": (datetime.now() + timedelta(minutes=30)).isoformat()
        }
    
    def verify_callback(self, callback_data: Dict) -> Tuple[bool, Dict]:
        return_code = callback_data.get('return_code', '')
        result_code = callback_data.get('result_code', '')
        is_success = return_code == 'SUCCESS' and result_code == 'SUCCESS'
        
        return is_success, {
            "order_id": callback_data.get('out_trade_no'),
            "transaction_id": callback_data.get('transaction_id'),
            "amount": float(callback_data.get('total_fee', 0)) / 100,
            "status": "success" if is_success else "failed"
        }


class StripeGateway(BasePaymentGateway):
    """Stripe支付网关"""
    
    def __init__(self, config: Dict):
        self.api_key = config.get('api_key', '')
        self.webhook_secret = config.get('webhook_secret', '')
    
    def create_order(self, order_data: Dict) -> Dict:
        """创建Stripe支付会话"""
        session_id = f"cs_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "order_id": order_data["order_id"],
            "session_id": session_id,
            "checkout_url": f"https://checkout.stripe.com/pay/{session_id}",
            "amount": order_data["amount"],
            "expired_at": (datetime.now() + timedelta(hours=2)).isoformat()
        }
    
    def verify_callback(self, callback_data: Dict) -> Tuple[bool, Dict]:
        return True, {
            "order_id": callback_data.get('client_reference_id'),
            "transaction_id": callback_data.get('payment_intent'),
            "amount": callback_data.get('amount_total', 0) / 100,
            "status": "success"
        }


class PaymentService:
    """统一支付服务"""
    
    GATEWAYS = {
        "alipay": AlipayGateway,
        "wechat": WechatPayGateway,
        "stripe": StripeGateway
    }
    
    def __init__(self, gateway_config: Dict = None):
        self.gateways = {}
        if gateway_config:
            for name, config in gateway_config.items():
                if name in self.GATEWAYS:
                    self.gateways[name] = self.GATEWAYS[name](config)
    
    def create_payment(self, order_data: Dict, payment_method: str) -> Dict:
        if payment_method not in self.gateways:
            raise PaymentError("UNSUPPORTED_METHOD", f"不支持的支付方式: {payment_method}")
        
        gateway = self.gateways[payment_method]
        return gateway.create_order(order_data)
    
    def handle_callback(self, payment_method: str, callback_data: Dict) -> Tuple[bool, Dict]:
        if payment_method not in self.gateways:
            raise PaymentError("UNSUPPORTED_METHOD", f"不支持的支付方式: {payment_method}")
        
        gateway = self.gateways[payment_method]
        return gateway.verify_callback(callback_data)
    
    def refund_payment(self, payment_method: str, order_id: str, amount: float, reason: str = None) -> Dict:
        return {
            "order_id": order_id,
            "refund_id": f"REF_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "amount": amount,
            "status": "success"
        }
