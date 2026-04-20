"""
数据库初始化脚本
用于 Railway PostgreSQL 数据库初始化
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()


def get_database_url():
    """获取数据库连接URL"""
    return os.environ.get('DATABASE_URL', '')


def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    db_url = get_database_url()
    if not db_url:
        print("警告: DATABASE_URL 未设置，跳过数据库创建")
        return
    
    # 解析数据库URL
    # postgresql://user:pass@host:5432/dbname
    try:
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        
        db_name = parsed.path.lstrip('/')
        db_user = parsed.username
        db_pass = parsed.password
        db_host = parsed.hostname
        db_port = parsed.port or 5432
        
        # 连接到默认数据库来创建新数据库
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_pass,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE {db_name}')
            print(f"数据库 '{db_name}' 创建成功")
        else:
            print(f"数据库 '{db_name}' 已存在")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"创建数据库时出错: {e}")


def init_schema():
    """初始化数据库表结构"""
    db_url = get_database_url()
    if not db_url:
        print("警告: DATABASE_URL 未设置，跳过表结构初始化")
        return
    
    # 读取SQL文件
    sql_file_path = os.path.join(os.path.dirname(__file__), 'database', 'membership_schema.sql')
    
    if not os.path.exists(sql_file_path):
        print(f"警告: SQL文件不存在: {sql_file_path}")
        return
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor.execute(sql_content)
        conn.commit()
        
        print("数据库表结构初始化成功")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"初始化表结构时出错: {e}")


def init_sample_data():
    """初始化示例数据"""
    db_url = get_database_url()
    if not db_url:
        return
    
    sample_data = """
    -- 插入示例会员权益
    INSERT INTO membership_benefits (level, benefit_name, benefit_value, description) VALUES
    ('free', 'ocr_daily_limit', '3', '每日OCR识别次数限制'),
    ('monthly', 'ocr_daily_limit', '50', '每月会员每日OCR识别次数限制'),
    ('yearly', 'ocr_daily_limit', '200', '年度会员每日OCR识别次数限制'),
    ('lifetime', 'ocr_daily_limit', 'unlimited', '终身会员无限OCR识别')
    ON CONFLICT (level, benefit_name) DO NOTHING;
    
    -- 插入示例优惠券
    INSERT INTO coupons (code, discount_type, discount_value, min_purchase, max_uses, applicable_products, valid_from, valid_until) VALUES
    ('WELCOME20', 'percentage', 20.00, 9.9, 100, '["monthly", "yearly"]', NOW(), NOW() + INTERVAL '30 days'),
    ('FIRST50', 'fixed', 50.00, 99.0, 50, '["yearly"]', NOW(), NOW() + INTERVAL '7 days')
    ON CONFLICT (code) DO NOTHING;
    """
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute(sample_data)
        conn.commit()
        
        print("示例数据初始化成功")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"初始化示例数据时出错: {e}")


def main():
    """主函数"""
    print("=" * 50)
    print("开始初始化 Railway PostgreSQL 数据库...")
    print("=" * 50)
    
    create_database_if_not_exists()
    init_schema()
    init_sample_data()
    
    print("=" * 50)
    print("数据库初始化完成！")
    print("=" * 50)


if __name__ == '__main__':
    main()
