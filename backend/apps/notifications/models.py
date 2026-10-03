from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    KIND_PRICE_DROP = "price_drop"
    KIND_NEW_LOT = "new_lot"
    KIND_ENQUIRY = "enquiry"
    KIND_MESSAGE = "message"
    KIND_APPROVAL = "approval"
    KIND_SYSTEM = "system"
    KIND_CHOICES = (
        (KIND_PRICE_DROP, _("Price drop")),
        (KIND_NEW_LOT, _("New lot")),
        (KIND_ENQUIRY, _("Enquiry")),
        (KIND_MESSAGE, _("New message")),
        (KIND_APPROVAL, _("Approval")),
        (KIND_SYSTEM, _("System")),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    url = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return f"{self.kind} → {self.recipient}"