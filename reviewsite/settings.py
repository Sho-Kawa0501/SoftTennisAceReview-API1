from pathlib import Path
import os
from datetime import timedelta 
import dj_database_url
import environ
import boto3

import logging


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = 'RENDER' not in os.environ
DEBUG = True


SECRET_KEY = os.environ.get('SECRET_KEY', default=os.environ['SECRET_KEY'])

ALLOWED_HOSTS = [
    'https://www.softtennis-ace-review.com',
    'https://softtennis-ace-review.com',
    'https://www.soft-tennis-star-review.com',
    'https://soft-tennis-star-review.com',
    '127.0.0.1',
    'softtennis-ace-review.com',
    'soft-tennis-star-review.com',
    'http://127.0.0.1:3000',
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'review',
    'account',
    'item',
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework_simplejwt.token_blacklist',
    'storages',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:3000',
    'http://localhost:3000',
    'https://www.softtennis-ace-review.com',
    'https://softtennis-ace-review.com',
]

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:3000',
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://www.softtennis-ace-review.com',
    'https://softtennis-ace-review.com',
]

CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:3000',
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://www.softtennis-ace-review.com',
    'https://softtennis-ace-review.com',
]

ROOT_URLCONF = 'reviewsite.urls'

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

WSGI_APPLICATION = 'reviewsite.wsgi.application'

# デバッグTrue
# Database
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT'),
        }
    }
else:
    # DATABASES = {"default": dj_database_url.config()}
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
# DATABASES = {
#     'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
# }


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DATETIME_FORMAT': '%Y/%m/%d %H:%M',
}

# デバッグTrue
# if not DEBUG:
JWT_AUTH_SECURE = True
JWT_AUTH_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'
SECURE_SSL_REDIRECT = True
# else:
#     # 開発環境の場合の設定
#     JWT_AUTH_SECURE = False
#     JWT_AUTH_SAMESITE = 'Lax'
#     SESSION_COOKIE_SECURE = False
#     CSRF_COOKIE_SECURE = False
#     SESSION_COOKIE_SAMESITE = 'Lax'

# REST_USE_JWT = True
JWT_AUTH_COOKIE = 'jwt-auth'
# JWT_AUTH_SECURE = True
# JWT_AUTH_SAMESITE = 'None'
# SESSION_COOKIE_SAMESITE = 'None'
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SAMESITE = 'None'
# CSRF_COOKIE_SECURE = True

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer','JWT',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken', ),
    'AUTH_COOKIE': 'jwt-auth',
    'AUTH_COOKIE_HTTP_ONLY': True,
}

AUTH_USER_MODEL = 'account.CustomUser'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

#render専用？
# if not DEBUG:
#     # Tell Django to copy statics to the `staticfiles` directory
#     # in your application directory on Render.
#     STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


    # STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

# Django-Storage

# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


# AWS-Settings
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_LOCATION = 'static' # s3バケット上のベースとなるファイルパス
AWS_S3_REGION_NAME=os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_URL = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_SIGNATURE_VERSION = 's3v4'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static'),
]

AWS_QUERYSTRING_AUTH = True
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
AWS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
}

STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
MEDIA_ROOT = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/{MEDIAFILES_LOCATION}/'

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
STATIC_ROOT = 'https://%s/%s/static/' % (AWS_S3_CUSTOM_DOMAIN,STATICFILES_LOCATION)

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "file_overwrite": False,
            "default_acl": None,
            "querystring_auth": False,
            "object_parameters": {
                "CacheControl": "max-age=86400",
            },
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}

# STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'
# MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'
# STATIC_URL = 'https://%s.s3.ap-northeast-1.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
# AWS_S3_BUCKET_NAME_STATIC = os.environ.get('AWS_STORAGE_BUCKET_NAME')

# STATIC_URL = '/static/'

# MEDIA_URL = '/media/' 
# MEDIA_ROOT = str(BASE_DIR / 'media') 

# STATIC-Files
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SUPERUSER_EMAIL = env('SUPERUSER_EMAIL')
SUPERUSER_PASSWORD = env('SUPERUSER_PASSWORD')

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logfile.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}

logger = logging.getLogger(__name__)
logger.debug(f"DEBUG mode is {'on' if DEBUG else 'off'}")