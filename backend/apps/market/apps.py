from django.apps import AppConfig


class MarketConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.market"

    def ready(self):
        # Import signals to ensure they are registered
        import apps.market.signals  # noqa: F401
