"""
================================================================================
文件：settings.py
路径：/home/edo/cimf-v2/cimf_django/settings.py
================================================================================

功能说明：
    Django 项目配置文件，包含应用设置、数据库、模板引擎等配置。

版本：
    - 1.0: 初始版本

依赖：
    - django: 6.0+
    - djangorestframework: 用于 REST API
    - jinja2: 模板引擎（兼容现有模板）
"""

from pathlib import Path

# pymysql 兼容性处理（使用 MySQL 时需要）
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# 加载环境变量
import os

from dotenv import load_dotenv

from cimf_django.database import get_database_config

# 尝试加载 config.env 文件
load_dotenv(Path(__file__).resolve().parent.parent / 'config.env')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 确保必要的存储目录存在（首次部署时自动创建）
_storage_dirs = ['storage/logs', 'storage/uploads', 'storage/backups']
for _dir in _storage_dirs:
    (BASE_DIR / _dir).mkdir(parents=True, exist_ok=True)

# SECURITY WARNING: keep the secret key used in production secret!
# 从环境变量读取，如果不存在则使用默认值（仅用于开发）
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-9dtjvn^e5l-o7k12i*0_2ez**pbtje4ik=v*)a42t+r=n2rt#l'
)

# SECURITY WARNING: don't run with debug turned on in production!
# 调试模式：从环境变量读取，默认开启（开发环境）
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'

# 允许访问的主机列表：从环境变量读取，逗号分隔
# 用于 Django Host 头校验，防止 HTTP Host 头攻击。
# 也作为 IP 白名单的第二来源（中间件自动提取其中的 IP 地址）。
ALLOWED_HOSTS_STR = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]

# ----- IP 访问限制配置 -----
# IPWhitelistMiddleware 据此限制客户端 IP 来源。
# 白名单来源优先级：
#   1. DJANGO_IP_WHITELIST（显式配置，支持 CIDR 段）
#   2. DJANGO_ALLOWED_HOSTS（自动提取其中的 IP 地址，域名被静默跳过）
# 详见 cimf_django/middleware.py IPWhitelistMiddleware.__init__。
IP_RESTRICTION_ENABLED = os.getenv('DJANGO_IP_RESTRICTION_ENABLED', 'false').lower() == 'true'
_ip_whitelist_str = os.getenv('DJANGO_IP_WHITELIST', '').strip()
IP_WHITELIST = [ip.strip() for ip in _ip_whitelist_str.split(',') if ip.strip()]

# Application definition

# 基础应用（必须保留）
_base_apps = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'core.smtp',
    'modules',
]

# 动态扫描 modules/ 下的模块模板目录（仅用于模板加载，不添加到 INSTALLED_APPS）
_module_template_dirs = []
_nodes_dir = BASE_DIR / 'modules'
if _nodes_dir.is_dir():
    for item in _nodes_dir.iterdir():
        if item.is_dir():
            template_dir = item / 'templates'
            if template_dir.is_dir():
                _module_template_dirs.append(template_dir)

# 动态扫描并添加 modules/ 下的子模块到 INSTALLED_APPS
_module_apps = []
_nodes_dir = BASE_DIR / 'modules'
if _nodes_dir.is_dir():
    for item in _nodes_dir.iterdir():
        if item.is_dir():
            apps_path = item / 'apps.py'
            if apps_path.exists():
                _module_apps.append(f'modules.{item.name}')

INSTALLED_APPS = _base_apps + _module_apps

MIDDLEWARE = [
    'cimf_django.middleware.IPWhitelistMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cimf_django.middleware.GlobalLoginRequiredMiddleware',  # 全局登录要求
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cimf_django.urls'

# Jinja2 模板引擎配置（兼容现有 Flask 模板）
# 动态收集所有模板目录
_template_dirs = [BASE_DIR / 'core' / 'templates', *_module_template_dirs]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': _template_dirs,
        'APP_DIRS': False,
        'OPTIONS': {
            'environment': 'cimf_django.jinja2.environment',
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cimf_django.context_processors.system_settings',
                'cimf_django.context_processors.csrf_token',
                'cimf_django.context_processors.user_permissions',
            ],
            'extensions': [
                'jinja2.ext.loopcontrols',
                'jinja2.ext.do',
                'jinja2.ext.i18n',
                # 'jinja2.ext.debug',  # 禁用调试扩展
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': _template_dirs,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cimf_django.context_processors.system_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'cimf_django.wsgi.application'

# Database - 根据 config.env 配置选择 SQLite 或 MySQL
DATABASES = {
    'default': get_database_config()
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'storage' / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'storage' / 'uploads'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Auth 配置
AUTH_USER_MODEL = 'core.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Django REST Framework 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
    'VERSION_PARAM': 'version',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '200/hour',
        'login': '10/minute',
        'admin': '1000/hour',
    },
}

# Flash/Toast 消息配置
MESSAGE_TAGS = {
    'debug': 'alert-info',
    'info': 'alert-info',
    'success': 'alert-success',
    'warning': 'alert-warning',
    'error': 'alert-danger',
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {funcName} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'storage' / 'logs' / 'cimf.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
            'formatter': 'verbose',
            'level': 'INFO',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'storage' / 'logs' / 'error.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'storage' / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
            'level': 'INFO',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'modules': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 自定义错误页面处理（跟随主题）
handler400 = 'core.views.errors.error_400'
handler403 = 'core.views.errors.error_403'
handler404 = 'core.views.errors.error_404'
handler500 = 'core.views.errors.error_500'

# ----- 安全配置（从环境变量读取）-----
# 环境标识：development 或 production
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')

# HSTS (HTTP Strict Transport Security) 配置
SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('DJANGO_HSTS_INCLUDE_SUBDOMAINS', 'false').lower() == 'true'
SECURE_HSTS_PRELOAD = os.getenv('DJANGO_HSTS_PRELOAD', 'false').lower() == 'true'

# SSL 重定向
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SSL_REDIRECT', 'false').lower() == 'true'

# Cookie 安全设置
SESSION_COOKIE_SECURE = os.getenv('DJANGO_SESSION_COOKIE_SECURE', 'false').lower() == 'true'
CSRF_COOKIE_SECURE = os.getenv('DJANGO_CSRF_COOKIE_SECURE', 'false').lower() == 'true'

# 生产环境自动启用安全配置
if DJANGO_ENV == 'production':
    SECURE_HSTS_SECONDS = SECURE_HSTS_SECONDS or 31536000  # 默认1年
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    DEBUG = False
    if ALLOWED_HOSTS == ['localhost', '127.0.0.1']:
        raise ValueError("生产环境必须在 DJANGO_ALLOWED_HOSTS 中配置实际域名！")
