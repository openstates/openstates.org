import os
import dj_database_url
import structlog
import sentry_sdk
from corsheaders.defaults import default_headers
from sentry_sdk.integrations.django import DjangoIntegration

if "SENTRY_DSN" in os.environ:
    sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], integrations=[DjangoIntegration()])


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                )
            ],
        },
    }
]

if os.environ.get("MANAGEMENT_COMMAND_ONLY"):
    DEBUG = False
    ALLOWED_HOSTS = ["*"]
    SECRET_KEY = os.environ.get("SECRET_KEY", "non-secret-key")
    SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]
elif os.environ.get("DEBUG", "true").lower() == "false":
    # non-debug settings
    DEBUG = False
    ALLOWED_HOSTS = ["*"]
    ADMINS = [("James Turk", "james@openstates.org")]
    # DOMAIN = ''
    SECRET_KEY = os.environ["SECRET_KEY"]
    EMAIL_HOST = os.environ["EMAIL_HOST"]
    EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
    EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
    EMAIL_PORT = "587"
    EMAIL_USE_TLS = True
    REGISTRATION_DEFAULT_FROM_EMAIL = (
        DEFAULT_FROM_EMAIL
    ) = SERVER_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "contact@openstates.org")
    RECAPTCHA_PUBLIC_KEY = os.environ["RECAPTCHA_PUBLIC_KEY"]
    RECAPTCHA_PRIVATE_KEY = os.environ["RECAPTCHA_PRIVATE_KEY"]
    RECAPTCHA_USE_SSL = True
    # enable once SSL is ready
    # SECURE_HSTS_SECONDS = 3600
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
else:
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "non-secret-key")
    ALLOWED_HOSTS = ["*"]
    INTERNAL_IPS = ["127.0.0.1"]
    DOMAIN = "http://localhost:8000"
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    REGISTRATION_DEFAULT_FROM_EMAIL = "contact@openstates.org"
    # disable template caching
    TEMPLATES[0]["OPTIONS"]["loaders"] = [
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    ]
    if "RECAPTCHA_PUBLIC_KEY" in os.environ:
        RECAPTCHA_PUBLIC_KEY = os.environ["RECAPTCHA_PUBLIC_KEY"]
    if "RECAPTCHA_PRIVATE_KEY" in os.environ:
        RECAPTCHA_PRIVATE_KEY = os.environ["RECAPTCHA_PRIVATE_KEY"]
    else:
        SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgis://openstates:openstates@db:5432/openstatesorg"
)
DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
CONN_MAX_AGE = 60

if "CACHE_URL" in os.environ:
    CACHES = {
        "default": {
            "BACKEND": "redis_cache.RedisCache",
            "LOCATION": os.environ["CACHE_URL"],
        }
    }

STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.sites",
    "webpack_loader",
    "captcha",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.twitter",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.github",
    "openstates.data",
    "openstates.reports",
    "boundaries",
    "geo",
    "graphene_django",
    "public",
    "graphapi",
    "v1",
    "bulk",
    "profiles.apps.ProfilesConfig",
    "bundles",
    "dashboards",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "profiles.middleware.structlog_middleware",
]

ROOT_URLCONF = "web.urls"
WSGI_APPLICATION = "web.wsgi.application"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


SITE_ID = 1

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = "/static/"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static/"),)

STATIC_ROOT = os.path.join(BASE_DIR, "collected_static")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# redefine entire logging tree
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            # "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "graphapi": {"handlers": ["console"], "level": "DEBUG", "propagate": True},
        "openstates": {"handlers": ["console"], "level": "DEBUG", "propagate": True},
    },
}

# allauth backends
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)


# Django Webpack Loader Settings
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(BASE_DIR, "webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    }
}

# allauth
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_FORM_CLASS = "profiles.forms.AllauthSignupForm"

# Boundaries
BOUNDARIES_SHAPEFILES_DIR = "shapefiles"


# API
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r"^/(graphql|api/v1).*$"
CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS"]
CORS_ALLOW_HEADERS = default_headers + ("x-api-key",)


GRAPHENE = {"SCHEMA": "graphapi.schema.schema", "MIDDLEWARE": []}


# structlog config
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
