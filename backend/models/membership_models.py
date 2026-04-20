"""
会员付费系统 - 数据模型
定义用户、订单、会员权益等核心数据结构
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid


class MembershipLevel(Enum):
    """会员等级枚举"""
    FREE = "free"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


# ========== 定价方案（可切换） ==========
# 方案A：超低价引流
PRICING_PLAN_A = {
    "monthly": 2.0,      # ¥2/月
    "yearly": 19.9,      # ¥19.9/年
    "lifetime": 39.9     # ¥39.9/终身
}

# 方案B：平衡型（推荐）
PRICING_PLAN_B = {
    "monthly": 9.9,      # ¥9.9/月
    "yearly": 49.0,      # ¥49/年（月均¥4.1）
    "lifetime": 149.0    # ¥149/终身
}

# 方案C：盈利型
PRICING_PLAN_C = {
    "monthly": 19.9,     # ¥19.9/月
    "yearly": 99.0,      # ¥99/年
    "lifetime": 199.0    # ¥199/终身
}

# 当前使用的定价方案
PRODUCT_PRICES = PRICING_PLAN_B  # 切换方案只需改这里

# 会员权益配置
MEMBERSHIP_BENEFITS = {
    "free": {
        "problems_limit": 100,
        "ocr_daily_limit": 5,
        "analysis_depth": "basic",
        "discussion_access": "read_only",
        "recommendation_level": "basic",
        "report_access": False,
        "expansion_access": False,
        "api_access": False
    },
    "monthly": {
        "problems_limit": 500,
        "ocr_daily_limit": 50,
        "analysis_depth": "deep",
        "discussion_access": "full",
        "recommendation_level": "smart",
        "report_access": "monthly",
        "expansion_access": False,
        "api_access": False
    },
    "yearly": {
        "problems_limit": -1,  # 全部题库(2000+)
        "ocr_daily_limit": -1,  # 无限
        "analysis_depth": "complete",
        "discussion_access": "full",
        "recommendation_level": "ai",
        "report_access": "detailed",
        "expansion_access": True,  # 可扩充至4000+题
        "api_access": False
    },
    "lifetime": {
        "problems_limit": -1,
        "ocr_daily_limit": -1,
        "analysis_depth": "complete",
        "discussion_access": "full",
        "recommendation_level": "ai",
        "report_access": "detailed",
        "expansion_access": True,
        "api_access": True,
        "priority_support": True
    }
}


@dataclass
class User:
    """用户数据模型"""
    id: str
    username: str
    email: str
    level: str = "free"
    level_expires: Optional[datetime] = None
    ocr_count_today: int = 0
    ocr_count_date: Optional[date] = None
    total_problems_accessed: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def is_membership_active(self) -> bool:
        """检查会员是否有效"""
        if self.level in ["free", "lifetime"]:
            return True
        if self.level_expires is None:
            return False
        return datetime.now() < self.level_expires
    
    def get_current_level(self) -> str:
        """获取当前有效等级"""
        if not self.is_membership_active():
            return "free"
        return self.level
    
    def get_benefits(self) -> Dict[str, Any]:
        """获取用户当前权益"""
        current_level = self.get_current_level()
        return MEMBERSHIP_BENEFITS.get(current_level, MEMBERSHIP_BENEFITS["free"]).copy()
    
    def can_use_ocr(self) -> bool:
        """检查是否能使用OCR"""
        benefits = self.get_benefits()
        limit = benefits.get("ocr_daily_limit", 5)
        if limit == -1:
            return True
        self._reset_daily_ocr_if_needed()
        return self.ocr_count_today < limit
    
    def use_ocr(self) -> int:
        """使用一次OCR，返回剩余次数"""
        if not self.can_use_ocr():
            raise PermissionError("今日OCR次数已用完")
        self._reset_daily_ocr_if_needed()
        self.ocr_count_today += 1
        return self.get_remaining_ocr()
    
    def get_remaining_ocr(self) -> int:
        """获取剩余OCR次数"""
        benefits = self.get_benefits()
        limit = benefits.get("ocr_daily_limit", 5)
        if limit == -1:
            return -1  # 无限
        self._reset_daily_ocr_if_needed()
        return max(0, limit - self.ocr_count_today)
    
    def _reset_daily_ocr_if_needed(self):
        """如果日期变化，重置OCR计数"""
        today = date.today()
        if self.ocr_count_date is None or self.ocr_count_date < today:
            self.ocr_count_today = 0
            self.ocr_count_date = today


@dataclass
class Order:
    """订单数据模型"""
    order_id: str
    user_id: str
    product: str
    amount: float
    payment_method: str
    status: str = "pending"
    coupon_code: Optional[str] = None
    discount_amount: float = 0.0
    final_amount: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None
    transaction_id: Optional[str] = None
    
    @staticmethod
    def generate_order_id() -> str:
        """生成唯一订单号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD_{timestamp}_{unique_id}"


@dataclass
class Coupon:
    """优惠券数据模型"""
    code: str
    discount_type: str  # "percentage" 或 "fixed"
    discount_value: float
    min_purchase: Optional[float] = None
    applicable_products: Optional[List[str]] = None
    max_uses: int = -1
    current_uses: int = 0
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """检查优惠券是否有效"""
        now = datetime.now()
        if self.max_uses != -1 and self.current_uses >= self.max_uses:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True
