from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from apps.notifications.models import Notification


@login_required
def notification_list(request):
    """List all notifications for the current user."""
    notifications = Notification.objects.filter(recipient=request.user).order_by("-created_at")
    unread_count = notifications.filter(is_read=False).count()
    return render(
        request,
        "notifications/notification_list.html",
        {"notifications": notifications, "unread_count": unread_count},
    )


@login_required
def notification_mark_read(request, pk):
    """Mark a single notification as read."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    if notification.url:
        return redirect(notification.url)
    return redirect("notifications:list")


@login_required
def notification_mark_all_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect("notifications:list")
