"""
Django settings for school assessment project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Only load this project's environment, including when launched from an IDE.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env', override=True)
APP_INSTANCE_NAME = os.getenv('APP_INSTANCE_NAME', 'xiangmu2')

# 导入Celery应用
from .celery import app as celery_app

__all__ = ('celery_app',)

# Build paths inside the project

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方应用
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    
    # 本地应用
    'apps.accounts',
    'apps.schools',
    'apps.assessments',
    'apps.surveys',
    'apps.reports',
    'apps.admin_panel',
    'apps.regions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # CSRF中间件 - API使用JWT认证，不需要CSRF保护
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CSRF配置
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5174',
    'http://127.0.0.1:5174',
    'http://localhost:8001',
    'http://127.0.0.1:8001',
]
SESSION_COOKIE_NAME = f'{APP_INSTANCE_NAME}_sessionid'
CSRF_COOKIE_NAME = f'{APP_INSTANCE_NAME}_csrftoken'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'xiangmu2'),
        'USER': os.getenv('DB_USER', 'xiangmu2_local'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'TEST': {'NAME': f'{APP_INSTANCE_NAME}_test'},
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
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
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 自定义用户模型
AUTH_USER_MODEL = 'accounts.User'

# REST Framework配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    # 禁用CSRF验证（因为使用JWT认证）
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

# JWT配置
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Redis配置
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6380))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Django缓存配置（使用django-redis）
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ['REDIS_CACHE_URL'],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50}
        },
        'KEY_PREFIX': APP_INSTANCE_NAME,
        'TIMEOUT': 300,
    }
}

# Celery配置
CELERY_BROKER_URL = os.environ['CELERY_BROKER_URL']
CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
CELERY_TASK_DEFAULT_QUEUE = APP_INSTANCE_NAME
CELERY_TASK_DEFAULT_EXCHANGE = APP_INSTANCE_NAME
CELERY_TASK_DEFAULT_ROUTING_KEY = APP_INSTANCE_NAME
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# 邮件配置
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.qq.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '1546414461@qq.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 系统配置
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5174')
SYSTEM_EMAIL_SIGNATURE = '此邮件由系统自动发送，请勿回复'

# 大模型API配置（可选，也可在数据库中配置）
LLM_API_PROVIDER = os.getenv('LLM_API_PROVIDER', 'openai')
LLM_ALLOW_NETWORK = os.getenv('LLM_ALLOW_NETWORK', 'False').lower() == 'true'
LLM_API_KEY = os.getenv('LLM_API_KEY', '')
LLM_API_ENDPOINT = os.getenv('LLM_API_ENDPOINT', 'https://api.openai.com/v1')
LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME', 'gpt-3.5-turbo')

# DeepSeek API配置（使用OpenAI SDK）
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_ENDPOINT = 'https://api.deepseek.com'  # base_url不需要完整路径
DEEPSEEK_MODEL_NAME = os.getenv('DEEPSEEK_MODEL_NAME', 'deepseek-chat')

# 阿里云OSS配置
ALIYUN_OSS_ACCESS_KEY_ID = os.getenv('ALIYUN_OSS_ACCESS_KEY_ID', '')
ALIYUN_OSS_ACCESS_KEY_SECRET = os.getenv('ALIYUN_OSS_ACCESS_KEY_SECRET', '')
ALIYUN_OSS_ENDPOINT = os.getenv('ALIYUN_OSS_ENDPOINT', 'https://oss-cn-beijing.aliyuncs.com')
ALIYUN_OSS_BUCKET_NAME = os.getenv('ALIYUN_OSS_BUCKET_NAME', 'mature')
ALIYUN_OSS_CNAME = os.getenv('ALIYUN_OSS_CNAME', '')  # 自定义域名，可选

# 使用OSS作为文件存储（使用自定义存储后端，兼容Django 4.x）
USE_OSS = os.getenv('USE_OSS', 'False').lower() == 'true'
if USE_OSS and ALIYUN_OSS_ACCESS_KEY_ID and ALIYUN_OSS_ACCESS_KEY_SECRET:
    DEFAULT_FILE_STORAGE = 'utils.oss_storage.AliyunOSSStorage'
    # 构建MEDIA_URL
    endpoint_host = ALIYUN_OSS_ENDPOINT.replace('https://', '').replace('http://', '')
    MEDIA_URL = f'https://{ALIYUN_OSS_BUCKET_NAME}.{endpoint_host}/'
    if ALIYUN_OSS_CNAME:
        MEDIA_URL = f'{ALIYUN_OSS_CNAME}/'

# 日志配置
(BASE_DIR / 'logs').mkdir(exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
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
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
