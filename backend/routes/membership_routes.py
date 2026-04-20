"""
会员管理路由
提供会员相关的API接口
"""
from flask import Blueprint, request, jsonify, g
from ..membership.service import create_membership_service
from ..membership.decorators import require_membership, require_ocr_usage
from ..membership.benefits import BenefitsManager

membership_bp = Blueprint('membership', __name__, url_prefix='/api/membership')

# 初始化服务
service = create_membership_service()


@membership_bp.route('/status', methods=['GET'])
def get_membership_status():
    """获取会员状态"""
    # 实际项目中从session获取user_id
    user_id = request.args.get('user_id', 'user_demo')
    
    try:
        status = service.get_user_membership_status(user_id)
        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@membership_bp.route('/pricing', methods=['GET'])
def get_pricing():
    """获取定价信息"""
    cards = BenefitsManager.get_pricing_cards()
    
    return jsonify({
        "success": True,
        "data": {
            "products": cards,
            "payment_methods": ["alipay", "wechat", "stripe"]
        }
    })


@membership_bp.route('/purchase', methods=['POST'])
def create_purchase():
    """创建购买订单"""
    data = request.get_json()
    
    user_id = data.get('user_id', 'user_demo')
    product = data.get('product')
    payment_method = data.get('payment_method', 'alipay')
    coupon_code = data.get('coupon_code')
    
    if not product:
        return jsonify({
            "success": False,
            "message": "请选择会员产品"
        }), 400
    
    try:
        result = service.create_order(user_id, product, payment_method, coupon_code)
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@membership_bp.route('/callback/<payment_method>', methods=['POST'])
def payment_callback(payment_method):
    """支付回调"""
    callback_data = request.get_json()
    
    try:
        result = service.handle_payment_callback(payment_method, callback_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@membership_bp.route('/orders', methods=['GET'])
def get_orders():
    """获取用户订单列表"""
    user_id = request.args.get('user_id', 'user_demo')
    
    orders = service.get_user_orders(user_id)
    
    return jsonify({
        "success": True,
        "data": orders
    })


@membership_bp.route('/coupon/validate', methods=['POST'])
def validate_coupon():
    """验证优惠券"""
    data = request.get_json()
    
    code = data.get('code')
    product = data.get('product')
    amount = data.get('amount', 0)
    
    if not code:
        return jsonify({
            "success": False,
            "message": "请输入优惠码"
        }), 400
    
    is_valid, result = service.validate_coupon(code, product, amount)
    
    return jsonify({
        "success": is_valid,
        "data": result if is_valid else None,
        "message": result.get("error") if not is_valid else None
    })


@membership_bp.route('/expand/problems', methods=['POST'])
def expand_problems():
    """题库扩充"""
    data = request.get_json()
    user_id = data.get('user_id', 'user_demo')
    
    try:
        result = service.expand_problems(user_id)
        return jsonify({
            "success": True,
            "data": result
        })
    except PermissionError as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "upgrade_required": "yearly"
        }), 403
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@membership_bp.route('/refund', methods=['POST'])
def request_refund():
    """申请退款"""
    data = request.get_json()
    
    order_id = data.get('order_id')
    reason = data.get('reason')
    
    if not order_id:
        return jsonify({
            "success": False,
            "message": "请提供订单号"
        }), 400
    
    try:
        result = service.request_refund(order_id, reason)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@membership_bp.route('/upgrade-path', methods=['GET'])
def get_upgrade_path():
    """获取升级路径"""
    user_id = request.args.get('user_id', 'user_demo')
    
    user = service.get_user(user_id)
    if not user:
        return jsonify({
            "success": False,
            "message": "用户不存在"
        }), 404
    
    current_level = user.get_current_level()
    upgrades = BenefitsManager.get_upgrade_path(current_level)
    
    return jsonify({
        "success": True,
        "data": {
            "current_level": current_level,
            "upgrades": upgrades
        }
    })
