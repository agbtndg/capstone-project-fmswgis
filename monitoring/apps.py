from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'
    
    def ready(self):
        # Import template tags to ensure they're registered
        import monitoring.templatetags.custom_filters  # noqa
