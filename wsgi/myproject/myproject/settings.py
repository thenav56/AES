"""
Django settings for Project project.

Generated by 'django-admin startproject' using Django 1.9.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ksx*c7a)1oycdb2(5ze$v***xhlgvw+xq6uv$iwa5@y!2k_8n='

on_openshift = False
if 'OPENSHIFT_APP_NAME' in os.environ:
    on_openshift = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# if on_openshift:
    # DEBUG = False
# ALLOWED_HOSTS = ['localhost', '127.0.0.1']

if on_openshift:
    ALLOWED_HOSTS = ['aes-navinir.rhcloud.com', 'aes.navinayer.com.np']


# Application definition

INSTALLED_APPS = [
    # 'aes.apps.AesConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'essay',
    # 'rest_framework',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

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

from django.template.base import add_to_builtins
add_to_builtins('django.contrib.staticfiles.templatetags.staticfiles')
add_to_builtins('essay.templatetags.assign')


WSGI_APPLICATION = 'myproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
if on_openshift:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            'NAME':     os.environ['OPENSHIFT_GEAR_NAME'],
            'USER':     os.environ['OPENSHIFT_MYSQL_DB_USERNAME'],
            'PASSWORD': os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'],
            'HOST':     os.environ['OPENSHIFT_MYSQL_DB_HOST'],
            'PORT':     os.environ['OPENSHIFT_MYSQL_DB_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            # 'ENGINE': 'django.db.backends.mysql',
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            # 'NAME':     'aes',
            # 'USER':     'root',
            # 'PASSWORD': 'password',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Media Root and Url
if on_openshift:
    MEDIA_ROOT = os.path.join(os.environ.get('OPENSHIFT_DATA_DIR', ''), 'media')
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/static/'
if on_openshift:
    STATIC_ROOT = os.path.join(os.environ['OPENSHIFT_REPO_DIR'], 'static')
else:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), os.path.join(os.environ['PWD'],'../static/'),]

# REST_FRAMEWORK = {
    # 'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    # 'PAGE_SIZE': 10
# }
