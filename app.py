"""
Flask 应用入口 - 数学证明导师会员系统
支持 Railway 部署配置
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from backend.routes.membership_routes import membership_bp


def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # ========== Railway 兼容配置 ==========
    # Railway 会通过环境变量 PORT 提供端口
    app.config['PORT'] = int(os.environ.get('PORT', 5000))
    
    # Flask 密钥配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 数据库配置 - Railway PostgreSQL
    database_url = os.environ.get('DATABASE_URL', '')
    if database_url:
        # Railway PostgreSQL 使用 postgres:// 协议
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # 本地开发使用 SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///membership.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CORS 配置
    cors_origins = os.environ.get('CORS_ORIGINS', '*')
    if cors_origins == '*':
        CORS(app)
    else:
        CORS(app, origins=cors_origins.split(','))
    
    # 注册蓝图
    app.register_blueprint(membership_bp)
    
    # ========== 路由定义 ==========
    
    @app.route('/')
    def index():
        """首页"""
        return render_template('index.html')
    
    @app.route('/membership')
    def membership_page():
        """会员页面"""
        return render_template('pages/membership.html')
    
    @app.route('/pricing')
    def pricing_page():
        """价格页面"""
        return render_template('pages/pricing.html')
    
    @app.route('/my-membership')
    def my_membership_page():
        """我的会员页面"""
        return render_template('pages/my-membership.html')
    
    # ========== 健康检查端点（Railway 需要） ==========
    
    @app.route('/health')
    def health_check():
        """健康检查端点"""
        return jsonify({
            'status': 'healthy',
            'service': 'math-tutor-membership',
            'version': '1.0.0'
        })
    
    # ========== 支付回调路由 ==========
    
    @app.route('/pay/callback/alipay', methods=['POST'])
    def alipay_callback():
        """支付宝回调"""
        from backend.membership import create_membership_service
        from flask import request
        
        service = create_membership_service()
        callback_data = request.form.to_dict()
        
        result = service.handle_payment_callback('alipay', callback_data)
        
        if result['success']:
            return 'success'
        return 'fail'
    
    @app.route('/pay/callback/wechat', methods=['POST'])
    def wechat_callback():
        """微信支付回调"""
        from backend.membership import create_membership_service
        from flask import request, Response
        import xml.etree.ElementTree as ET
        
        service = create_membership_service()
        
        # 解析XML
        xml_data = request.data
        root = ET.fromstring(xml_data)
        callback_data = {child.tag: child.text for child in root}
        
        result = service.handle_payment_callback('wechat', callback_data)
        
        if result['success']:
            return Response('<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>', 
                           mimetype='text/xml')
        return Response('<xml><return_code><![CDATA[FAIL]]></return_code></xml>', 
                       mimetype='text/xml')
    
    return app


# 创建应用实例
app = create_app()


# ========== Railway 启动入口 ==========
# Railway 会通过 gunicorn 启动，忽略此块
if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    app.run(debug=False, host='0.0.0.0', port=port)
