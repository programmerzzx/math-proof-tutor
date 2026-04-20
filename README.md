# 数学证明导师 - 会员付费系统

一个完整的会员付费系统，支持题库扩充、高级功能解锁等付费服务。

## 🎯 价格体系

| 会员等级 | 价格 | 亮点 |
|---------|------|------|
| **免费版** | ¥0 | 100题 + 每日5次OCR |
| **月度会员** | ¥2/月 | 买杯奶茶都不够！|
| **年度会员** ⭐ | ¥19.9/年 | 最划算·性价比之王 |
| **终身会员** | ¥39.9 | 一次付费永久使用 |

## ✨ 会员权益

### 免费版
- ✅ 100道基础题
- ✅ 每日5次OCR识别
- ✅ 基础分析功能
- ❌ 深度分析
- ❌ 题库扩充

### 月度会员（¥2/月）
- ✅ 500道题目
- ✅ 每日50次OCR
- ✅ 深度分析+失分点
- ✅ 学习报告
- ❌ 题库扩充

### 年度会员（¥19.9/年）⭐ 推荐
- ✅ 全部题库（2000+题）
- ✅ 无限次OCR
- ✅ 完整分析+知识图谱
- ✅ **题库扩充（扩充至4000+题）**
- ✅ 详细学习报告

### 终身会员（¥39.9）
- ✅ 年度会员所有权益
- ✅ 永久访问权限
- ✅ API接口权限
- ✅ 优先客服支持
- ✅ 新功能抢先体验

## 📁 项目结构

```
会员付费系统/
├── backend/
│   ├── membership/
│   │   ├── __init__.py       # 模块初始化
│   │   ├── service.py        # 会员服务核心逻辑
│   │   ├── payment.py        # 支付网关集成
│   │   ├── benefits.py       # 权益管理
│   │   └── decorators.py     # 权限装饰器
│   ├── routes/
│   │   └── membership_routes.py  # API路由
│   └── models/
│       └── membership_models.py  # 数据模型
├── frontend/
│   ├── pages/
│   │   └── membership.html   # 会员购买页面
│   └── scripts/
│       └── membership.js     # 前端SDK
├── database/
│   └── membership_schema.sql # 数据库脚本
└── README.md
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install flask
```

### 2. 初始化数据库

```bash
mysql -u root -p < database/membership_schema.sql
```

### 3. 配置支付

编辑 `backend/membership/payment.py` 配置您的支付网关：

```python
gateway_config = {
    "alipay": {
        "app_id": "your_app_id",
        "private_key": "your_private_key",
        "alipay_public_key": "alipay_public_key"
    },
    "wechat": {
        "app_id": "your_app_id",
        "mch_id": "your_mch_id",
        "api_key": "your_api_key"
    }
}
```

### 4. 启动服务

```python
from flask import Flask
from backend.routes.membership_routes import membership_bp

app = Flask(__name__)
app.register_blueprint(membership_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## 📡 API 接口

### 获取会员状态
```
GET /api/membership/status?user_id=xxx
```

### 获取定价信息
```
GET /api/membership/pricing
```

### 创建订单
```
POST /api/membership/purchase
{
    "user_id": "xxx",
    "product": "yearly",
    "payment_method": "alipay",
    "coupon_code": "WELCOME"
}
```

### 支付回调
```
POST /api/membership/callback/{payment_method}
```

### 验证优惠券
```
POST /api/membership/coupon/validate
{
    "code": "WELCOME",
    "product": "yearly",
    "amount": 19.9
}
```

### 题库扩充
```
POST /api/membership/expand/problems
{
    "user_id": "xxx"
}
```

## 💳 支付集成

系统支持三种支付方式：

### 支付宝
- 扫码支付
- APP支付
- 网页支付

### 微信支付
- 扫码支付
- APP支付

### Stripe
- 信用卡支付
- 全球覆盖

## 🎨 前端集成

```html
<!-- 引入SDK -->
<script src="/frontend/scripts/membership.js"></script>

<script>
// 显示购买弹窗
MembershipSDK.showPaymentModal('yearly', 19.9, '年度会员');

// 创建订单
const result = await MembershipSDK.createOrder(
    'user_123',
    'yearly',
    'alipay'
);
</script>
```

## 🔐 权限装饰器

```python
from backend.membership import require_membership

@app.route('/api/premium-feature')
@require_membership('yearly')
def premium_feature():
    return jsonify({"success": True})
```

## 📊 数据库

系统使用以下数据表：

- `users` - 用户表
- `orders` - 订单表
- `membership_benefits` - 会员权益配置表
- `coupons` - 优惠券表
- `subscriptions` - 订阅记录表
- `invoices` - 发票表

## 🛡️ 安全特性

- ✅ 支付签名验证
- ✅ 订单状态校验
- ✅ 会员权限控制
- ✅ 退款时限控制（7天）
- ✅ SQL注入防护
- ✅ XSS防护

## 📈 扩展功能

- [ ] 自动续费
- [ ] 发票自动开具
- [ ] 会员等级折扣
- [ ] 邀请返现
- [ ] 学习数据统计

## 📄 License

MIT License
