from pathlib import Path
import os
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-t&e=3!z+m_^q@khmqc)%@i02!yt^rd#yg%a!&)-5gkr+=%uuy@'

SECRET_KEY= os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']


# Application definition

INSTALLED_APPS = [
    'uvicorn',
    'channels',
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_standardized_errors',
    'drf_spectacular',
    'django_celery_beat',
]

PROJECT_APPS = ['users']

INSTALLED_APPS += PROJECT_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'middleware.loggingmiddleware.LogRestMiddleware',
]

ROOT_URLCONF = 'backend_bolt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

AUTH_USER_MODEL= 'users.User'

# WSGI_APPLICATION = 'backend_bolt.wsgi.application'
ASGI_APPLICATION = 'backend_bolt.asgi.application'

# Database
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT")

# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": DB_HOST, # "127.0.0.1", # 
        "NAME": DB_NAME, # "bolt", # 
        "USER": DB_USER, # "postgres", # 
        "PASSWORD": DB_PASSWORD, # "postgres", # 
        "PORT": DB_PORT, # "5432", # 
        # "CONN_MAX_AGE": 0,
        # "POOL_OPTIONS": {
        #     "POOL_SIZE": 20,
        #     "MAX_OVERFLOW": 10,
        #     "RECYCLE": 24 * 60 * 60,
        # },
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

DRF_STANDARDIZED_ERRORS = {
    "ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": True,
    "EXCEPTION_HANDLER_CLASS": "exception_handling.exception_formatter.CustomExceptionHandler",
    "EXCEPTION_FORMATTER_CLASS": "exception_handling.exception_formatter.CustomExceptionFormatter",
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT= BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=120),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Backend-Bolt',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')   #'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST') # 'sandbox.smtp.mailtrap.io'  'smtp.gmail.com'
EMAIL_PORT = os.getenv('EMAIL_PORT') # 587
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') # True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER') #  '75783219c1923e'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD') # 'bad0bcf76b8bdf'

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL') # "redis://localhost:6379/0" # 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SYNC_ON_STARTUP = False

# channel layer
# ASGI_APPLICATION= "myproject.asgi.application"
CHANNEL_LAYERS= {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            # "hosts": [("redis", 6379)], # For docker 
        }
    }
}

CORS_ORIGIN_ALLOW_ALL = True

# LOG_DIR = os.path.join(BASE_DIR, 'logs')
# ARC_DIR= os.path.join(BASE_DIR, 'archive')

# os.makedirs(LOG_DIR, exist_ok= True)
# os.makedirs(ARC_DIR, exist_ok= True)

from users.log import LOGGING_DICT
LOGGING_CONFIG = 'logging.config.dictConfig'
LOGGING = LOGGING_DICT