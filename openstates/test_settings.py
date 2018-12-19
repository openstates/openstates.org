from .settings import *  # noqa

SIMPLEKEYS_ZONE_PATHS = []

MIDDLEWARE_REMOVE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]
MIDDLEWARE = [m for m in MIDDLEWARE if m not in MIDDLEWARE_REMOVE]      # noqa
