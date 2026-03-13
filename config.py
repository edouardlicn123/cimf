# config.py
import os
from pathlib import Path
import secrets
from datetime import timedelta
from typing import Any

# 项目根目录（从 config.py 向上两级，通常是 run.py 所在目录）
BASE_DIR = Path(__file__).resolve().parent

# 调试：打印实际使用的项目根目录（开发时有用，生产可注释）
if os.environ.get('FLASK_ENV', 'development').lower() == 'development':
    print(f"[DEBUG] 项目根目录 (BASE_DIR): {BASE_DIR}")
    print(f"[DEBUG] 数据库预期路径: {BASE_DIR / 'instance' / 'site.db'}")

class BaseConfig:
    """基础配置 - 所有环境共用"""

    # 项目根目录（供其他地方使用）
    BASE_DIR = BASE_DIR

    # =============================================
    # 核心安全 - SECRET_KEY（最高优先级）
    # =============================================
    SECRET_KEY = (
        os.environ.get('SECRET_KEY')
        or os.environ.get('FLASK_SECRET_KEY')
        or secrets.token_urlsafe(48)  # 推荐 64+ 字符
    )

    # 随机密钥警告逻辑
    _using_random_key = not (os.environ.get('SECRET_KEY') or os.environ.get('FLASK_SECRET_KEY'))
    if _using_random_key:
        msg = (
            f"[{os.getenv('START_TIME', 'unknown')}] "
            "【严重安全警告】未设置 SECRET_KEY，使用临时随机密钥！\n"
            "  → 生产环境必须通过环境变量提供固定强密钥\n"
            "  生成命令：python -c \"import secrets; print(secrets.token_urlsafe(48))\""
        )
        if os.environ.get('FLASK_ENV') == 'production':
            raise RuntimeError(msg)
        print(msg)

    # =============================================
    # 数据库 - 强制使用项目根下的 instance/site.db
    # =============================================
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        f"sqlite:///{BASE_DIR / 'instance' / 'site.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
    }

    # =============================================
    # 数据库初始化模式控制
    # =============================================
    # DB_INIT_MODE: 控制应用启动时的数据库初始化行为
    #   - 'none': 不自动初始化（使用 Flask-Migrate，适合生产环境）
    #   - 'auto': 自动创建表 + 种子数据（适合开发环境）
    #   - 'schema_only': 仅创建表结构
    #
    # 环境变量: DB_INIT_MODE
    # 默认值: none（生产安全优先）
    DB_INIT_MODE = os.environ.get('DB_INIT_MODE', 'none')

    # DB_SEED_DATA: 是否初始化种子数据（仅 DB_INIT_MODE='auto' 时有效）
    #   - true: 初始化种子数据（管理员账号、系统设置、词汇表等）
    #   - false: 仅创建表结构
    #
    # 环境变量: DB_SEED_DATA
    # 默认值: true
    DB_SEED_DATA = os.environ.get('DB_SEED_DATA', 'true').lower() in ('true', '1', 'yes')

    # 开发时可选开启 SQL 日志（取消注释即可）
    # if os.environ.get('FLASK_ENV', 'development').lower() == 'development':
    #     SQLALCHEMY_ECHO = True

    # =============================================
    # 文件上传 - 统一放在项目根下 persistent_uploads
    # =============================================
    UPLOAD_FOLDER = str(BASE_DIR / 'persistent_uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'docx', 'csv'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MiB

    # =============================================
    # 会话 & Cookie 安全
    # =============================================
    SESSION_COOKIE_NAME = 'ffe_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)

    # =============================================
    # 分页 & 业务通用
    # =============================================
    ITEMS_PER_PAGE = 20
    DEFAULT_PAGE_SIZE = 20
    MAX_PROJECT_NAME_LENGTH = 120
    MAX_USERNAME_LENGTH = 64

    # =============================================
    # 其他 Flask 推荐配置
    # =============================================
    JSON_SORT_KEYS = False
    JSON_AS_ASCII = False
    PROPAGATE_EXCEPTIONS = True


class DevelopmentConfig(BaseConfig):
    ENV = 'development'
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    PREFERRED_URL_SCHEME = 'http'
    DB_INIT_MODE = 'auto'  # 开发环境自动初始化
    DB_SEED_DATA = True    # 开发环境包含种子数据
    TEMPLATES_AUTO_RELOAD = True  # 开发环境自动重载模板


class TestingConfig(BaseConfig):
    ENV = 'testing'
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 86400
    DB_INIT_MODE = 'none'  # 生产环境禁用自动初始化
    DB_SEED_DATA = False

    if BaseConfig._using_random_key:
        raise RuntimeError(
            "生产环境必须通过环境变量 SECRET_KEY 设置强密钥！\n"
            "禁止使用随机生成的临时密钥。"
        )


# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}


def get_config() -> type[BaseConfig]:
    """根据环境变量返回配置类"""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    return config.get(env, config['default'])
