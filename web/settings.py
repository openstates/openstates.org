import os
import dj_database_url
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if "SENTRY_DSN" in os.environ:
    sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], integrations=[DjangoIntegration()])

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


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


if os.environ.get("DEBUG", "true").lower() == "false":
    # non-debug settings
    DEBUG = False
    ALLOWED_HOSTS = ["*"]
    ADMINS = [("James Turk", "james@openstates.org")]
    SECRET_KEY = os.environ["SECRET_KEY"]
    OPENSTATES_API_KEY = os.environ["OPENSTATES_API_KEY"]
    MAPBOX_ACCESS_TOKEN = os.environ["MAPBOX_ACCESS_TOKEN"]
else:
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "non-secret-key")
    ALLOWED_HOSTS = ["*"]
    INTERNAL_IPS = ["127.0.0.1"]
    DOMAIN = "http://localhost:8000"
    # disable template caching
    TEMPLATES[0]["OPTIONS"]["loaders"] = [
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    ]
    OPENSTATES_API_KEY = os.environ.get("OPENSTATES_API_KEY")
    MAPBOX_ACCESS_TOKEN = os.environ.get("MAPBOX_ACCESS_TOKEN")

# Login Notes
#  This site has an unorthodox setup where the login is handled by openstates.org
#  This has a few components:
#   1) openstates.org has to set a SESSION_COOKIE_DOMAIN that is permissive enough that the
#       cookie will be sent to widgets.openstates.org
#   2) This site has to know enough about allauth that when it gets the session key it looks
#       things up in the correct database tables.
#   3) Both sites have to share a SECRET_KEY setting, any changes would require redeployment
#       of both.
#  See notes in rest of file tagged LOGIN for places where this is done.

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://openstates:openstates@db:5432/openstatesorg"
)
DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
CONN_MAX_AGE = 60

SITE_ID = 1
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # LOGIN: these are needed so that when the session is passed it has something to look up
    # "django.contrib.sites",
    # "allauth",
    # "allauth.account",
    # "allauth.socialaccount",
    "widgets",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# LOGIN: allauth backends
if not DEBUG:
    AUTHENTICATION_BACKENDS = (
        "django.contrib.auth.backends.ModelBackend",
        "allauth.account.auth_backends.AuthenticationBackend",
    )
    SESSION_COOKIE_DOMAIN = "openstates.org"

ROOT_URLCONF = "web.urls"
WSGI_APPLICATION = "web.wsgi.application"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_L10N = False
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "build",
    BASE_DIR / "static",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "collected_static/"
