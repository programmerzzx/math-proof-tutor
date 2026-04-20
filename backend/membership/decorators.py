"""
会员权限装饰器
"""
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime
from .benefits import BenefitsManager


def require_membership(min_level: str, error_message: str = None):
    """会员等级验证装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            
            if user is None:
                return jsonify({"error": "unauthorized", "message": "请先登录"}), 401
            
            user_level = user.get_current_level()
            
            if not BenefitsManager.is_higher_or_equal(user_level, min_level):
                return jsonify({
                    "error": "membership_required",
                    "message": error_message or f"此功能需要{BenefitsManager.get_level_display_name(min_level)}",
                    "required_level": min_level,
                    "current_level": user_level,
                    "upgrade_path": BenefitsManager.get_upgrade_path(user_level)
                }), 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_ocr_usage(func):
    """OCR使用验证装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = getattr(g, 'current_user', None)
        
        if user is None:
            return jsonify({"error": "unauthorized", "message": "请先登录"}), 401
        
        user._reset_daily_ocr_if_needed()
        
        if not user.can_use_ocr():
            benefits = user.get_benefits()
            limit = benefits.get("ocr_daily_limit", 5)
            
            return jsonify({
                "error": "ocr_limit_exceeded",
                "message": "今日OCR次数已用完，请升级会员获取更多次数",
                "used_today": user.ocr_count_today,
                "daily_limit": limit,
                "upgrade_path": BenefitsManager.get_upgrade_path(user.level)
            }), 429
        
        remaining = user.use_ocr()
        
        response = func(*args, **kwargs)
        if hasattr(response, 'headers'):
            response.headers['X-OCR-Remaining'] = str(remaining)
        
        return response
    
    return wrapper


class MembershipGuard:
    """会员权限守卫类"""
    
    def __init__(self, user):
        self.user = user
    
    @property
    def level(self) -> str:
        return self.user.get_current_level()
    
    def can_access(self, min_level: str) -> bool:
        return BenefitsManager.is_higher_or_equal(self.level, min_level)
    
    def get_user_info(self) -> dict:
        benefits = self.user.get_benefits()
        
        return {
            "user_id": self.user.id,
            "level": self.user.level,
            "effective_level": self.level,
            "is_active": self.user.is_membership_active(),
            "expires_at": self.user.level_expires.isoformat() if self.user.level_expires else None,
            "benefits": benefits,
            "ocr_remaining": self.user.get_remaining_ocr(),
            "pricing": BenefitsManager.get_pricing_cards()
        }
    
    def get_upgrade_recommendations(self) -> List[dict]:
        recommendations = []
        
        if not self.can_access("monthly"):
            recommendations.append({
                "target": "monthly",
                "price": 2,
                "tag": "买杯奶茶都不够",
                "features": ["500道题", "每日50次OCR", "深度分析"]
            })
        
        if not self.can_access("yearly"):
            recommendations.append({
                "target": "yearly",
                "price": 19.9,
                "tag": "最划算·性价比之王",
                "features": ["全部题库(2000+)", "无限OCR", "题库扩充"]
            })
        
        if not self.can_access("lifetime"):
            recommendations.append({
                "target": "lifetime",
                "price": 39.9,
                "tag": "一次付费永久使用",
                "features": ["永久年度权益", "API权限", "优先支持"]
            })
        
        return recommendations
