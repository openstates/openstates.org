from django.apps import AppConfig


class AdmintoolsConfig(AppConfig):
    name = 'admintools'

    def ready(self):
        from admintools import issues
        # Initialazing Issues
        issues.main()
