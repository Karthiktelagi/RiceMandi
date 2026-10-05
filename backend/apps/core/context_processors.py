"""Template context processors for global data."""
from django.conf import settings as app_settings
from apps.notifications.models import Notification


def unread_notifications(request):
    """Add unread notification count to every template context."""
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    else:
        count = 0
    return {"unread_notifications": count}


def site_settings(request):
    """Expose feature flags so templates can render conditionally."""
    google = app_settings.SOCIALACCOUNT_PROVIDERS.get("google", {}).get("APP", {})
    google_enabled = bool(google.get("client_id") and google.get("secret"))
    return {"google_login_enabled": google_enabled}
