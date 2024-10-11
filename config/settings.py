"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path

import yaml
from decouple import config as decouple_config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def load_config():
    # 检查是否是生产环境
    if decouple_config('PRODUCTION', default=False, cast=bool):
        return {
            'SECRET_KEY': decouple_config('SECRET_KEY'),
            'DEBUG': decouple_config('DEBUG', cast=bool),
            'DATABASE': {
                'ENGINE': 'dj_db_conn_pool.backends.mysql',
                'NAME': decouple_config('DB_NAME'),
                'USER': decouple_config('DB_USER'),
                'PASSWORD': decouple_config('DB_PASSWORD'),
                'HOST': decouple_config('DB_HOST'),
                'PORT': decouple_config('DB_PORT', cast=int),
            },
            'CHROMA_CONFIG': {
                'HOST': decouple_config('CHROMA_SERVICE_HOST'),
                'PORT': decouple_config('CHROMA_SERVER_PORT', cast=int),
            },
            'REDIS_CONFIG': {
                'HOST': decouple_config('REDIS_HOST'),
                'PORT': decouple_config('REDIS_PORT', cast=int),
            }
        }
    else:
        # 读取测试环境配置文件
        with open('config.yaml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            return {
                'SECRET_KEY': data['secret_key'],
                'DEBUG': data['debug'],
                'DATABASE': {
                    'ENGINE': data['database']['engine'],
                    'NAME': data['database']['name'],
                    'USER': data['database']['user'],
                    'PASSWORD': data['database']['password'],
                    'HOST': data['database']['host'],
                    'PORT': data['database']['port'],
                },
                'CHROMA_CONFIG': {
                    'HOST': data['chroma']['host'],
                    'PORT': data['chroma']['port'],
                },
                'REDIS_CONFIG': {
                    'HOST': data['redis']['host'],
                    'PORT': data['redis']['port'],
                }
            }


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# 使用配置
config = load_config()
SECRET_KEY = config['SECRET_KEY']
DEBUG = config['DEBUG']
database_config = config['DATABASE']
database_config['OPTIONS'] = {
    'charset': 'utf8mb4',
}
DATABASES = {
    'default': database_config
}
CHROMA_CONFIG = config['CHROMA_CONFIG']

# if DEBUG:
#     ALLOWED_HOSTS = ['*']
# else:
#     ALLOWED_HOSTS = config['ALLOWED_HOSTS']

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.robot',
    'apps.user',
    'apps.face_recognition',
    'apps.product',
    'apps.shop',
    'apps.order',
    'apps.cart',
    'rest_framework',
    'rest_framework_simplejwt',
    'channels',
]

ASGI_APPLICATION = 'config.asgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(config['REDIS_CONFIG']['HOST'], config['REDIS_CONFIG']['PORT'])],
        },
    },
}

AUTH_USER_MODEL = 'user.User'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),  # 访问令牌有效期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # 刷新令牌有效期
    'ROTATE_REFRESH_TOKENS': True,  # 如果启用，刷新时刷新令牌也会被更新
    'BLACKLIST_AFTER_ROTATION': True,  # 刷新令牌旋转后加入黑名单
    'AUTH_HEADER_TYPES': ('Bearer',),
}

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
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

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

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

APPEND_SLASH = False
