"""
会员权益管理模块
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..models.membership_models import MembershipLevel, MEMBERSHIP_BENEFITS, PRODUCT_PRICES


class BenefitsManager:
    """权益管理器"""
    
    LEVEL_ORDER = ["free", "monthly", "yearly", "lifetime"]
    
    # 价格展示文案
    PRICE_TAGS = {
        "monthly": "买杯奶茶都不够",
        "yearly": "强烈推荐·性价比之王",
        "lifetime": "一次付费永久使用"
    }
    
    # 优惠标签
    DISCOUNT_TAGS = {
        "monthly": "超值",
        "yearly": "最划算",
        "lifetime": "永久权益"
    }
    
    @classmethod
    def get_all_levels(cls) -> List[str]:
        return cls.LEVEL_ORDER.copy()
    
    @classmethod
    def get_level_display_name(cls, level: str) -> str:
        names = {
            "free": "免费版",
            "monthly": "月度会员",
            "yearly": "年度会员",
            "lifetime": "终身会员"
        }
        return names.get(level, level)
    
    @classmethod
    def get_level_price(cls, level: str) -> float:
        return PRODUCT_PRICES.get(level, 0)
    
    @classmethod
    def get_price_tag(cls, level: str) -> str:
        return cls.PRICE_TAGS.get(level, "")
    
    @classmethod
    def get_discount_tag(cls, level: str) -> str:
        return cls.DISCOUNT_TAGS.get(level, "")
    
    @classmethod
    def get_benefits(cls, level: str) -> Dict[str, Any]:
        return MEMBERSHIP_BENEFITS.get(level, MEMBERSHIP_BENEFITS["free"]).copy()
    
    @classmethod
    def is_higher_or_equal(cls, user_level: str, required_level: str) -> bool:
        order_map = {"free": 0, "monthly": 1, "yearly": 2, "lifetime": 3}
        return order_map.get(user_level, 0) >= order_map.get(required_level, 0)
    
    @classmethod
    def get_upgrade_path(cls, current_level: str) -> List[Dict[str, Any]]:
        current_index = cls.LEVEL_ORDER.index(current_level) if current_level in cls.LEVEL_ORDER else 0
        upgrades = []
        
        for level in cls.LEVEL_ORDER[current_index + 1:]:
            upgrades.append({
                "level": level,
                "name": cls.get_level_display_name(level),
                "price": cls.get_level_price(level),
                "price_tag": cls.get_price_tag(level),
                "discount_tag": cls.get_discount_tag(level),
                "benefits": cls.get_benefits(level),
                "duration": cls.get_subscription_duration(level)
            })
        
        return upgrades
    
    @classmethod
    def get_subscription_duration(cls, level: str) -> str:
        durations = {
            "monthly": "1个月",
            "yearly": "1年",
            "lifetime": "永久"
        }
        return durations.get(level, "")
    
    @classmethod
    def calculate_expire_date(cls, product: str) -> Optional[datetime]:
        if product == "lifetime":
            return None
        now = datetime.now()
        if product == "monthly":
            return now + timedelta(days=30)
        elif product == "yearly":
            return now + timedelta(days=365)
        return None
    
    @classmethod
    def get_pricing_cards(cls) -> List[Dict[str, Any]]:
        """获取定价卡片数据（用于前端展示）"""
        cards = []
        
        # 免费版
        cards.append({
            "level": "free",
            "name": "免费版",
            "price": 0,
            "price_unit": "",
            "tag": None,
            "highlight": False,
            "recommended": False,
            "benefits": [
                {"text": "100道基础题", "included": True},
                {"text": "每日5次OCR", "included": True},
                {"text": "基础分析", "included": True},
                {"text": "深度分析", "included": False},
                {"text": "题库扩充", "included": False},
            ]
        })
        
        # 月度会员 ¥2
        cards.append({
            "level": "monthly",
            "name": "月度会员",
            "price": 2,
            "price_unit": "元/月",
            "tag": "买杯奶茶都不够",
            "tag_type": "slogan",
            "highlight": False,
            "recommended": False,
            "benefits": [
                {"text": "500道题目", "included": True},
                {"text": "每日50次OCR", "included": True},
                {"text": "深度分析+失分点", "included": True},
                {"text": "学习报告", "included": True},
                {"text": "题库扩充", "included": False},
            ]
        })
        
        # 年度会员 ¥19.9 ⭐推荐
        cards.append({
            "level": "yearly",
            "name": "年度会员",
            "price": 19.9,
            "price_unit": "元/年",
            "tag": "最划算",
            "tag_type": "badge",
            "highlight": True,
            "recommended": True,
            "benefits": [
                {"text": "全部题库(2000+题)", "included": True},
                {"text": "无限次OCR", "included": True},
                {"text": "完整分析+知识图谱", "included": True},
                {"text": "题库扩充(4000+题)", "included": True},
                {"text": "详细学习报告", "included": True},
            ]
        })
        
        # 终身会员 ¥39.9
        cards.append({
            "level": "lifetime",
            "name": "终身会员",
            "price": 39.9,
            "price_unit": "元/永久",
            "tag": "一次付费永久使用",
            "tag_type": "slogan",
            "highlight": False,
            "recommended": False,
            "benefits": [
                {"text": "年度会员所有权益", "included": True},
                {"text": "永久访问权限", "included": True},
                {"text": "API接口权限", "included": True},
                {"text": "优先客服支持", "included": True},
                {"text": "新功能抢先体验", "included": True},
            ]
        })
        
        return cards


class ProblemBankService:
    """题库服务"""
    
    def __init__(self):
        self.total_problems = 2000
        self.expanded_problems = 0
    
    def get_accessible_problems(self, user_level: str) -> Dict[str, Any]:
        benefits = BenefitsManager.get_benefits(user_level)
        limit = benefits.get("problems_limit", 100)
        
        accessible = self.total_problems
        can_expand = benefits.get("expansion_access", False)
        
        if limit == -1:
            accessible = self.total_problems + self.expanded_problems
        
        return {
            "accessible_count": min(accessible, limit if limit != -1 else accessible),
            "total_count": self.total_problems + self.expanded_problems,
            "expanded_count": self.expanded_problems,
            "can_expand": can_expand,
            "limit": limit,
            "is_unlimited": limit == -1
        }
    
    def expand_problem_bank(self, user_level: str) -> Dict[str, Any]:
        benefits = BenefitsManager.get_benefits(user_level)
        
        if not benefits.get("expansion_access", False):
            raise PermissionError("请升级至年度会员解锁题库扩充功能")
        
        new_problems = 2500  # 扩充至4000+题
        self.expanded_problems += new_problems
        
        return {
            "success": True,
            "new_problems": new_problems,
            "total_problems": self.total_problems + self.expanded_problems
        }


class OCRService:
    """OCR服务"""
    
    def check_limit(self, user_level: str, user_ocr_today: int, user_ocr_date: str) -> Dict[str, Any]:
        benefits = BenefitsManager.get_benefits(user_level)
        limit = benefits.get("ocr_daily_limit", 5)
        
        if limit == -1:
            return {
                "can_use": True,
                "remaining": -1,
                "is_unlimited": True,
                "limit": -1
            }
        
        today = date.today().isoformat()
        current_count = 0 if user_ocr_date != today else user_ocr_today
        remaining = max(0, limit - current_count)
        
        return {
            "can_use": remaining > 0,
            "remaining": remaining,
            "is_unlimited": False,
            "limit": limit,
            "used_today": current_count
        }


# 全局实例
benefits_manager = BenefitsManager()
problem_bank_service = ProblemBankService()
ocr_service = OCRService()
