"""Template context processors for global data."""
from apps.notifications.models import Notification


def unread_notifications(request):
    """Add unread notification count to every template context."""
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    else:
        count = 0
    return {"unread_notifications": count}
