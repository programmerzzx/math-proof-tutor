"""
会员模块初始化
"""
from .service import UserMembershipService, MembershipError, create_membership_service
from .benefits import BenefitsManager, problem_bank_service, ocr_service
from .payment import PaymentService, PaymentError
from .decorators import require_membership, require_ocr_usage, MembershipGuard
from ..models.membership_models import User, Order, Coupon, PRODUCT_PRICES, MEMBERSHIP_BENEFITS

__all__ = [
    'UserMembershipService', 'MembershipError', 'create_membership_service',
    'BenefitsManager', 'problem_bank_service', 'ocr_service',
    'PaymentService', 'PaymentError',
    'require_membership', 'require_ocr_usage', 'MembershipGuard',
    'User', 'Order', 'Coupon', 'PRODUCT_PRICES', 'MEMBERSHIP_BENEFITS'
]
