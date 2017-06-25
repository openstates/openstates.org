# not tests, just Django settings
SECRET_KEY = 'test'
INSTALLED_APPS = (
    'pupa',
    'admintools',
    'opencivicdata.core.apps.BaseConfig',
    'opencivicdata.legislative.apps.BaseConfig',
)
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'ocd_test_db_31',
        'USER': 'pupa',
        'PASSWORD': 'pupa',
        'HOST': 'localhost',
        'PORT': '',
    }
}
MIDDLEWARE_CLASSES = ()
