import os
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

if os.environ.get('DEBUG', 'true').lower() == 'false':
    # non-debug settings
    DEBUG = False
    ALLOWED_HOSTS = ['*']
    # DOMAIN = ''
    SECRET_KEY = os.environ['SECRET_KEY']
    # ADMINS list should be 'Name Email, Name Email, Name Email...'
    ADMINS = [a.rsplit(' ', 1) for a in os.environ.get('ADMINS', '').split(',')]
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = '587'
    EMAIL_USE_TLS = True
    REGISTRATION_DEFAULT_FROM_EMAIL = DEFAULT_FROM_EMAIL = SERVER_EMAIL = os.environ.get(
        'DEFAULT_FROM_EMAIL', 'contact@openstates.org')
    GRAPHQL_DEMO_KEY = os.environ['GRAPHQL_DEMO_KEY']
    # enable once SSL is ready
    # SECURE_HSTS_SECONDS = 3600
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
else:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'debug-secret-key')
    ALLOWED_HOSTS = ['*']
    INTERNAL_IPS = ['127.0.0.1']
    DOMAIN = 'http://localhost:8000'
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    REGISTRATION_DEFAULT_FROM_EMAIL = 'contact@openstates.org'
    # disable template caching
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]
    GRAPHQL_DEMO_KEY = 'graphiql-demo-key'

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'sqlite:///' + os.path.join(os.path.dirname(__file__), 'openstates.sqlite3')
)
DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
CONN_MAX_AGE = 60

if 'RAVEN_DSN' in os.environ:
    RAVEN_CONFIG = {
        'dsn': os.environ['RAVEN_DSN']
    }

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'raven.contrib.django.raven_compat',
    'webpack_loader',
    'opencivicdata.core.apps.BaseConfig',
    'opencivicdata.legislative.apps.BaseConfig',
    'boundaries',
    'geo',
    'pupa',
    'graphene_django',
    'public.apps.PublicConfig',
    'graphapi',
    'v1',
    'simplekeys',
    # 'silk',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simplekeys.middleware.SimpleKeysMiddleware',
    # 'silk.middleware.SilkyMiddleware',
]

ROOT_URLCONF = 'openstates.urls'
WSGI_APPLICATION = 'openstates.wsgi.application'


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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '/public/static/'),
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'graphapi': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# Django Webpack Loader Settings
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'public/bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}

# Boundaries
BOUNDARIES_SHAPEFILES_DIR = 'shapefiles'


# API
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/(graphql|api/v1)/.*$'
CORS_ALLOW_METHODS = ['GET', 'POST', 'OPTIONS']


GRAPHENE = {
    'SCHEMA': 'graphapi.schema.schema',
    'MIDDLEWARE': []
}

SIMPLEKEYS_ZONE_PATHS = [
    ('/api/v1/legislators/geo/', 'geo'),
    ('/api/v1/', 'default'),
]
SIMPLEKEYS_ERROR_NOTE = ('https://openstates.org/api/register/ for API key. '
                         'contact@openstates.org to raise limits')
