"""
Django settings for IDcard_recog project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import configparser
import json
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from bottle import response

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#  __file__指的是当前脚本


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y8(47d93%olhig)aj#6_kvdjwxkwbo=3ko9#1zz4==+et3g2v5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'idcard_ocr',
    'corsheaders'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 放到中间件顶部
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'IDcard_recog.MyMiddle.MyCorsMiddle'
    # 'IDcard_recog.SolveCrossDomain.SolveCrossDomainMiddleware'

]


ROOT_URLCONF = 'IDcard_recog.urls'

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
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True  # 允许任何区域访问
# 在某些url上使用这个跨域中间件
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ORIGIN_WHITELIST = (
    'http://192.168.48.160:8080',
    'http://192.168.0.118:8080',
    'http://*.*.*.*:*'
)
# 允许的http请求
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
]

# 允许的请求头
CORS_ALLOW_HEADERS = [
    'XMLHttpRequest',
    'X_FILENAME',
    'Pragma',
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Content-Type',
    'text/html'
]

WSGI_APPLICATION = 'IDcard_recog.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# 数据库的配置
config_init = configparser.ConfigParser()
config_init.read('E:\\IDcard_recog\\IDcard_recog\\IDcard_recog\\config\\config.ini')

config_Json = ''

with open('E:\\IDcard_recog\\IDcard_recog\\IDcard_recog\\config\\config.json', 'rt') as f:
    config_Json = json.load(f)

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': config_init.get("Mysql-Database", "host"),
        'PORT': config_init.get("Mysql-Database", "port"),
        'NAME': config_init.get("Mysql-Database", "name"),
        'USER': config_init.get("Mysql-Database", "user"),
        'PASSWORD': config_init.get("Mysql-Database", "password")
    },

    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': config_Json['Mysql-Database']['host'],
        'PORT': config_Json['Mysql-Database']['port'],
        'NAME': config_Json['Mysql-Database']['name'],
        'USER': config_Json['Mysql-Database']['user'],
        'PASSWORD': config_Json['Mysql-Database']['password']
    }
}

# 设置最大可以通过图片
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 默认设置为10M

