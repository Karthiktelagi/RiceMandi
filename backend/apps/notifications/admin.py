from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "kind", "title", "is_read", "created_at")
    list_filter = ("kind", "is_read")
    search_fields = ("recipient__username", "title", "body")
    readonly_fields = ("created_at",)
