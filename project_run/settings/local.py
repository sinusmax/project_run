from .base import *

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# добавил для django debug toolbar
INSTALLED_APPS.append('debug_toolbar')
MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = [
    '127.0.0.1',
    # '0.0.0.0', # Если нужно для других локальных сетей
]

# Добавил для включения Django Logger
# В консоли будут отображаться все запросы в БД
# После оптимизации лучше закомментировать
# ----------
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "level": "DEBUG",
#             "class": "logging.StreamHandler",
#         },
#     },
#     "loggers": {
#         "django.db.backends": {
#             "handlers": ["console"],
#             "level": "DEBUG",
#         },
#     },
# }
# ----------