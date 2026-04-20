/**
 * 会员系统 JavaScript SDK
 * 提供前端与后端会员API的交互封装
 */

const MembershipSDK = {
    // API基础URL
    baseURL: '/api/membership',
    
    /**
     * 获取会员状态
     */
    async getStatus(userId = 'user_demo') {
        try {
            const response = await fetch(`${this.baseURL}/status?user_id=${userId}`);
            const result = await response.json();
            return result.success ? result.data : null;
        } catch (error) {
            console.error('获取会员状态失败:', error);
            return null;
        }
    },
    
    /**
     * 获取定价信息
     */
    async getPricing() {
        try {
            const response = await fetch(`${this.baseURL}/pricing`);
            const result = await response.json();
            return result.success ? result.data : null;
        } catch (error) {
            console.error('获取定价信息失败:', error);
            return null;
        }
    },
    
    /**
     * 创建购买订单
     */
    async createOrder(userId, product, paymentMethod, couponCode = null) {
        try {
            const response = await fetch(`${this.baseURL}/purchase`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    product: product,
                    payment_method: paymentMethod,
                    coupon_code: couponCode
                })
            });
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('创建订单失败:', error);
            return { success: false, message: '网络错误' };
        }
    },
    
    /**
     * 验证优惠券
     */
    async validateCoupon(code, product, amount) {
        try {
            const response = await fetch(`${this.baseURL}/coupon/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: code,
                    product: product,
                    amount: amount
                })
            });
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('验证优惠券失败:', error);
            return { success: false, message: '网络错误' };
        }
    },
    
    /**
     * 获取订单列表
     */
    async getOrders(userId) {
        try {
            const response = await fetch(`${this.baseURL}/orders?user_id=${userId}`);
            const result = await response.json();
            return result.success ? result.data : [];
        } catch (error) {
            console.error('获取订单列表失败:', error);
            return [];
        }
    },
    
    /**
     * 申请题库扩充
     */
    async expandProblems(userId) {
        try {
            const response = await fetch(`${this.baseURL}/expand/problems`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_id: userId })
            });
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('题库扩充失败:', error);
            return { success: false, message: '网络错误' };
        }
    },
    
    /**
     * 申请退款
     */
    async requestRefund(orderId, reason = null) {
        try {
            const response = await fetch(`${this.baseURL}/refund`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    order_id: orderId,
                    reason: reason
                })
            });
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('申请退款失败:', error);
            return { success: false, message: '网络错误' };
        }
    },
    
    /**
     * 获取升级路径
     */
    async getUpgradePath(userId) {
        try {
            const response = await fetch(`${this.baseURL}/upgrade-path?user_id=${userId}`);
            const result = await response.json();
            return result.success ? result.data : null;
        } catch (error) {
            console.error('获取升级路径失败:', error);
            return null;
        }
    },
    
    /**
     * 显示购买弹窗
     */
    showPaymentModal(product, amount, productName) {
        const modal = document.getElementById('paymentModal');
        if (modal) {
            document.getElementById('modalTitle').textContent = productName + '开通';
            document.getElementById('modalAmount').textContent = amount;
            document.getElementById('confirmAmount').textContent = amount;
            modal.classList.add('active');
            
            // 保存当前产品信息
            this._currentProduct = product;
            this._currentAmount = amount;
        }
    },
    
    /**
     * 执行支付
     */
    async confirmPayment(paymentMethod, couponCode = null) {
        const userId = this._getCurrentUserId();
        const result = await this.createOrder(
            userId,
            this._currentProduct,
            paymentMethod,
            couponCode
        );
        
        if (result.success) {
            // 处理支付跳转
            if (result.data.qr_code_url) {
                this._showQRCode(result.data.qr_code_url);
            } else if (result.data.checkout_url) {
                window.location.href = result.data.checkout_url;
            }
        }
        
        return result;
    },
    
    /**
     * 获取当前用户ID（需根据实际实现）
     */
    _getCurrentUserId() {
        return localStorage.getItem('user_id') || 'user_demo';
    },
    
    /**
     * 显示二维码
     */
    _showQRCode(url) {
        alert('请使用微信扫码支付\n' + url);
    },
    
    /**
     * 渲染定价卡片
     */
    async renderPricingCards(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const pricing = await this.getPricing();
        if (!pricing) return;
        
        let html = '';
        pricing.products.forEach(product => {
            html += this._createPricingCard(product);
        });
        
        container.innerHTML = html;
    },
    
    /**
     * 创建定价卡片HTML
     */
    _createPricingCard(product) {
        const isRecommended = product.recommended;
        const badge = isRecommended ? '<div class="badge">⭐ 最划算</div>' : '';
        const tag = product.tag ? `<div class="slogan-tag">${product.tag}</div>` : '';
        const btnClass = isRecommended ? 'btn-recommended' : 'btn-buy';
        const btnText = isRecommended ? '立即开通' : (product.level === 'free' ? '当前方案' : '立即购买');
        
        let featuresHtml = '';
        product.benefits.forEach(benefit => {
            const icon = benefit.included ? '✓' : '✕';
            const iconClass = benefit.included ? 'check' : 'cross';
            featuresHtml += `
                <li>
                    <span class="icon ${iconClass}">${icon}</span>
                    ${benefit.text}
                </li>
            `;
        });
        
        return `
            <div class="pricing-card ${isRecommended ? 'recommended' : ''}">
                ${badge}
                ${tag}
                <div class="card-header">
                    <h3>${product.name}</h3>
                    <div class="price">
                        <span class="currency">¥</span>${product.price}
                        ${product.price_unit ? `<span class="unit">/${product.price_unit}</span>` : ''}
                    </div>
                </div>
                <ul class="features">
                    ${featuresHtml}
                </ul>
                <button class="btn ${btnClass}" 
                        onclick="MembershipSDK.showPaymentModal('${product.level}', ${product.price}, '${product.name}')">
                    ${btnText}
                </button>
            </div>
        `;
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MembershipSDK;
}
