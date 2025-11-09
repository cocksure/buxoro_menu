from pathlib import Path
import environ

env = environ.Env(
    DEBUG=(bool, False),  # Указываем тип и значение по умолчанию
)

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
# DEBUG = env('DEBUG', default=False)
DEBUG = True

TELEGRAM_TOKEN = env('TELEGRAM_TOKEN')


# OPENAI_API_KEY = env('OPENAI_API_KEY')
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    'https://4fe3-92-38-9-203.ngrok-free.app',  # Добавь сюда свой ngrok-адрес
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


    # local apps
    'menu',
    'corsheaders',
    'rest_framework',
    'django.contrib.humanize'

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'menu.middleware.SaveUserIdMiddleware',
    'menu.middleware.RateLimitMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True  # Разрешить все домены (для разработки)
CORS_ALLOW_CREDENTIALS = True  # Разрешить передачу куки


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SESSION_COOKIE_AGE = 500
SESSION_COOKIE_SAMESITE = 'Lax'  # Dlya prodashn nujno sdelat None
SESSION_COOKIE_SECURE = False  # Dlya prodakshn nujno sdelat True
# CSRF_COOKIE_SECURE = True  # CSRF-токены тоже должны быть защищены
SESSION_SAVE_EVERY_REQUEST = True
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

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

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

if DEBUG:
    # Настройки для разработки
    STATICFILES_DIRS = [BASE_DIR / 'static']
    # В DEBUG режиме staticfiles будет работать без collectstatic
    STATIC_ROOT = BASE_DIR / 'staticfiles'  # отдельная папка для collectstatic (если понадобится)
else:
    # Настройки для продакшена
    STATICFILES_DIRS = []
    STATIC_ROOT = BASE_DIR / 'static'

# Версионирование статических файлов (Django 4.2+)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # В DEBUG используем обычный StaticFilesStorage
        # В production - ManifestStaticFilesStorage для cache busting
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage" if DEBUG
                   else "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = env('MEDIA_ROOT', default=str(BASE_DIR / 'media'))

MEDIA_DIRS = [
    BASE_DIR / 'media',
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEFAULT_CHARSET = 'utf-8'