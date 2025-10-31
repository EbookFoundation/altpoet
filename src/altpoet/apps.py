from django.apps import AppConfig

class UserAgentCreationConfig(AppConfig):
    # default_auto_field = 'django.db.models.BigAutoField'
    name = 'altpoet'
    def ready(self):
        import altpoet.signals