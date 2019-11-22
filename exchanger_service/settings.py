"""
Django settings for exchanger_service project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'o1z(-b6&&su)(n)#(=*dhb%uj@lb+o2&%*_g!d2j^tzwvd4v!u'

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
    'exchanger.apps.ExchangerConfig',
    'rest_framework',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'exchanger_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'exchanger_service.wsgi.application'
TEST_MODE = False

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDATABASE') or 'exchanger',
        'USER': os.getenv('PGUSER') or os.getenv('LOGNAME', 'postgres'),
        'PASSWORD': os.getenv('PGPASSWORD') or os.getenv('LOGNAME', 'postgres'),
        'HOST': os.getenv('PGHOST') or '127.0.0.1',
        'PORT': 5432,
    },
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ]
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

GRPC_SERVER_PORT = '50054'
GRPC_TIMEOUT = 10  # default timeout for grpc requests
REMOTE_OPERATION_ATTEMPT_NUMBER = 3
ONE_DAY_IN_SECONDS = 60 * 60 * 24

# gateway addresses

WALLETS_GW_ADDRESS = 'localhost:50051'
TRANSACTIONS_GW_ADDRESS = 'localhost:50051'
CURRENCY_GW_ADDRESS = 'localhost:50051'
BLOCKCHAIN_GW_ADDRESS = 'localhost:50051'
MIN_FEE_LIMIT = 100  # in usd
DEFAULT_FEE = 5
EXTENDED_FEE = 10

TRX_FEE_DICT = {
    True: DEFAULT_FEE,  # in usd
    False: EXTENDED_FEE,  # in usd
}

ETH_ADDRESS = os.getenv('ETH_COLD_ADDRESS', '0xF6E4709341426Dee13c9e9EaB6e4779b299CE2F7')
BTC_ADDRESS = os.getenv('BTC_COLD_ADDRESS', 'mtQGkRpBVRDdRBwVkCbtGArdCYmiqkQrB1')
BTC_EXTERNAL_ID = os.getenv('BTC_EXTERNAL_ID', 23)
ETH_EXTERNAL_ID = os.getenv('ETH_EXTERNAL_ID', 24)

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
LOGFILE = 'exchanger.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple'
        },
        'file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'filename': LOGFILE,
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', 'file_handler'],
        },
        'django.request': {
            'handlers': ['file_handler', 'console'],
            'level': 'ERROR',
        },
        'exchanger': {
            'handlers': ['console', 'file_handler'],
            'level': 'DEBUG',
        },
    }
}

import sys
sys.path.append('/etc/bonum-exchanger')
sys.path.append(BASE_DIR + '/exchanger/rpc')

for path in (BASE_DIR, '/etc/bonum-exchanger'):
    if os.path.exists(os.path.join(path, 'local_settings.py')):
        from local_settings import *

if os.path.exists('exchanger_service/local_settings.py') or \
        os.path.exists('py-exchanger/exchanger_service/local_settings.py'):
    from exchanger_service.local_settings import *
