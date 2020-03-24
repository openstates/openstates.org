import os

from django.core.wsgi import get_wsgi_application

try:
    import newrelic.agent

    newrelic.agent.initialize()
    newrelic.agent.capture_request_params()
except Exception as e:
    print("newrelic couldn't be initialized:", e)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openstates.settings")

application = get_wsgi_application()
