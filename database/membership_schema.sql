-- ========================================
-- 数学证明导师 - 会员付费系统数据库
-- ========================================

-- 用户表（扩展）
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    level ENUM('free', 'monthly', 'yearly', 'lifetime') DEFAULT 'free',
    level_expires DATETIME,
    ocr_count_today INT DEFAULT 0,
    ocr_count_date DATE,
    total_problems_accessed INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_level (level),
    INDEX idx_level_expires (level_expires)
);

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    product ENUM('monthly', 'yearly', 'lifetime') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    final_amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('alipay', 'wechat', 'stripe') NOT NULL,
    status ENUM('pending', 'paid', 'failed', 'refunded', 'cancelled') DEFAULT 'pending',
    coupon_code VARCHAR(50),
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP,
    expired_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 会员权益表
CREATE TABLE IF NOT EXISTS membership_benefits (
    level ENUM('free', 'monthly', 'yearly', 'lifetime') NOT NULL,
    benefit_name VARCHAR(50) NOT NULL,
    benefit_value TEXT,
    description VARCHAR(255),
    PRIMARY KEY (level, benefit_name)
);

-- 优惠券表
CREATE TABLE IF NOT EXISTS coupons (
    code VARCHAR(50) PRIMARY KEY,
    discount_type ENUM('percentage', 'fixed') NOT NULL,
    discount_value DECIMAL(10, 2) NOT NULL,
    min_purchase DECIMAL(10, 2),
    max_uses INT DEFAULT -1,
    current_uses INT DEFAULT 0,
    applicable_products JSON,
    valid_from TIMESTAMP,
    valid_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_valid (valid_from, valid_until)
);

-- 订阅表
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    product ENUM('monthly', 'yearly', 'lifetime') NOT NULL,
    status ENUM('active', 'cancelled', 'expired') DEFAULT 'active',
    auto_renew BOOLEAN DEFAULT TRUE,
    next_billing_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_status (user_id, status)
);

-- 发票表
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    order_id VARCHAR(36) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    title VARCHAR(100) NOT NULL,
    tax_number VARCHAR(50),
    status ENUM('pending', 'issued', 'sent') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    issued_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- ========================================
-- 初始化数据
-- ========================================

-- 插入会员权益数据
INSERT INTO membership_benefits (level, benefit_name, benefit_value, description) VALUES
-- 免费版
('free', 'problems_limit', '100', '可访问题目数量'),
('free', 'ocr_daily_limit', '5', '每日OCR次数'),
('free', 'analysis_depth', 'basic', '分析深度'),
('free', 'discussion_access', 'read_only', '讨论区权限'),
('free', 'recommendation_level', 'basic', '推荐级别'),

-- 月度会员 ¥2/月
('monthly', 'problems_limit', '500', '可访问题目数量'),
('monthly', 'ocr_daily_limit', '50', '每日OCR次数'),
('monthly', 'analysis_depth', 'deep', '分析深度'),
('monthly', 'discussion_access', 'full', '讨论区权限'),
('monthly', 'recommendation_level', 'smart', '推荐级别'),
('monthly', 'report_access', 'monthly', '学习报告'),

-- 年度会员 ¥19.9/年
('yearly', 'problems_limit', '-1', '可访问题目数量（全部）'),
('yearly', 'ocr_daily_limit', '-1', '每日OCR次数（无限）'),
('yearly', 'analysis_depth', 'complete', '分析深度'),
('yearly', 'discussion_access', 'full', '讨论区权限'),
('yearly', 'recommendation_level', 'ai', '推荐级别'),
('yearly', 'report_access', 'detailed', '学习报告'),
('yearly', 'expansion_access', 'true', '题库扩充权限'),

-- 终身会员 ¥39.9
('lifetime', 'problems_limit', '-1', '可访问题目数量（全部）'),
('lifetime', 'ocr_daily_limit', '-1', '每日OCR次数（无限）'),
('lifetime', 'analysis_depth', 'complete', '分析深度'),
('lifetime', 'discussion_access', 'full', '讨论区权限'),
('lifetime', 'recommendation_level', 'ai', '推荐级别'),
('lifetime', 'report_access', 'detailed', '学习报告'),
('lifetime', 'expansion_access', 'true', '题库扩充权限'),
('lifetime', 'api_access', 'true', 'API接口权限'),
('lifetime', 'priority_support', 'true', '优先客服支持');

-- 插入示例优惠券
INSERT INTO coupons (code, discount_type, discount_value, min_purchase, max_uses, applicable_products, valid_from, valid_until) VALUES
('WELCOME', 'percentage', '10', NULL, 1000, NULL, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR)),
('STUDENT', 'percentage', '20', NULL, 500, '["monthly", "yearly", "lifetime"]', NOW(), DATE_ADD(NOW(), INTERVAL 6 MONTH)),
('FIRST50', 'fixed', '1', 2, 50, '["monthly"]', NOW(), DATE_ADD(NOW(), INTERVAL 3 MONTH));

-- ========================================
-- 视图定义
-- ========================================

-- 用户会员信息视图
CREATE OR REPLACE VIEW v_user_membership AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.level,
    u.level_expires,
    CASE 
        WHEN u.level = 'free' THEN TRUE
        WHEN u.level = 'lifetime' THEN TRUE
        WHEN u.level_expires > NOW() THEN TRUE
        ELSE FALSE
    END AS is_active,
    CASE 
        WHEN u.level = 'lifetime' THEN NULL
        WHEN u.level_expires IS NULL THEN 0
        ELSE DATEDIFF(u.level_expires, NOW())
    END AS days_remaining,
    mb.problems_limit,
    mb.ocr_daily_limit,
    mb.analysis_depth,
    u.ocr_count_today,
    u.ocr_count_date,
    CASE 
        WHEN mb.ocr_daily_limit = -1 THEN TRUE
        ELSE u.ocr_count_today < mb.ocr_daily_limit
    END AS can_use_ocr,
    CASE 
        WHEN mb.ocr_daily_limit = -1 THEN -1
        ELSE GREATEST(0, mb.ocr_daily_limit - u.ocr_count_today)
    END AS ocr_remaining
FROM users u
LEFT JOIN membership_benefits mb ON u.level = mb.level AND mb.benefit_name = 'problems_limit';

-- ========================================
-- 存储过程
-- ========================================

-- 重置每日OCR计数
DELIMITER //
CREATE PROCEDURE reset_daily_ocr_count(IN p_user_id VARCHAR(36))
BEGIN
    UPDATE users 
    SET ocr_count_today = 0, 
        ocr_count_date = CURDATE() 
    WHERE id = p_user_id 
    AND (ocr_count_date IS NULL OR ocr_count_date < CURDATE());
END //
DELIMITER ;

-- 升级会员
DELIMITER //
CREATE PROCEDURE upgrade_membership(
    IN p_user_id VARCHAR(36),
    IN p_product VARCHAR(20)
)
BEGIN
    DECLARE v_expires DATETIME;
    
    -- 计算过期时间
    SET v_expires = CASE p_product
        WHEN 'monthly' THEN DATE_ADD(NOW(), INTERVAL 1 MONTH)
        WHEN 'yearly' THEN DATE_ADD(NOW(), INTERVAL 1 YEAR)
        WHEN 'lifetime' THEN NULL
        ELSE NULL
    END;
    
    -- 更新用户等级
    UPDATE users 
    SET level = p_product,
        level_expires = v_expires,
        updated_at = NOW()
    WHERE id = p_user_id;
    
    -- 重置OCR计数
    CALL reset_daily_ocr_count(p_user_id);
END //
DELIMITER ;

-- ========================================
-- 触发器
-- ========================================

-- 订单支付后自动升级会员
DELIMITER //
CREATE TRIGGER after_order_paid
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    IF NEW.status = 'paid' AND OLD.status = 'pending' THEN
        CALL upgrade_membership(NEW.user_id, NEW.product);
        
        -- 创建订阅记录
        INSERT INTO subscriptions (subscription_id, user_id, product, status, next_billing_date)
        VALUES (
            CONCAT('SUB_', LEFT(UUID(), 12)),
            NEW.user_id,
            NEW.product,
            'active',
            CASE NEW.product
                WHEN 'monthly' THEN DATE_ADD(NOW(), INTERVAL 1 MONTH)
                WHEN 'yearly' THEN DATE_ADD(NOW(), INTERVAL 1 YEAR)
                ELSE NULL
            END
        );
    END IF;
END //
DELIMITER ;

-- 每日OCR计数重置（可通过定时任务调用）
DELIMITER //
CREATE EVENT IF NOT EXISTS event_reset_ocr_daily
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY
DO
BEGIN
    UPDATE users 
    SET ocr_count_today = 0,
        ocr_count_date = CURDATE()
    WHERE ocr_count_date < CURDATE();
END //
DELIMITER ;
