import os
from pathlib import Path

from django.conf.locale import LANG_INFO
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "apps",
    'django.contrib.humanize',
    "parler",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sababan.urls'
AUTH_USER_MODEL = 'apps.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'login'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sababan.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sababan',
        'USER': 'postgres',
        'PASSWORD': os.environ.get('PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

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

TIME_ZONE = 'Asia/Tashkent'
USE_TZ = True

LANGUAGE_CODE = 'uz'
USE_I18N = True

LANGUAGES = [
    ('uz', 'O‘zbek'),
    ('uz-cyrl', 'Ўзбекча (кирилл)'),
    ('ru', 'Русский'),
]

LANG_INFO_new = {
    'uz-cyrl': {
        'code': 'uz-cyrl',
        'name': 'Uzbek (Cyrillic)',
        'name_local': 'Ўзбекча',
    },
}
LANG_INFO.update(LANG_INFO_new)

PARLER_LANGUAGES = {
    None: (
        {'code': 'uz'},
        {'code': 'uz-cyrl'},
        {'code': 'ru'},
    ),
    'default': {
        'fallbacks': ['uz'],
        'hide_untranslated': False,
    }
}
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "apps/static",
]
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
CSRF_TRUSTED_ORIGINS = [
    'https://darryl-formalistic-grimly.ngrok-free.dev',
    'http://192.168.1.103:7777',
    'http://127.0.0.1:1909/',
]
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
