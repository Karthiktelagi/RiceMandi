from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.market.models import Lot


class Conversation(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations_as_buyer")
    merchant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations_as_merchant")
    lot = models.ForeignKey(Lot, on_delete=models.SET_NULL, null=True, blank=True, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ("buyer", "merchant", "lot")
        ordering = ["-last_message_at"]
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")

    def __str__(self):
        return f"{self.buyer} ↔ {self.merchant}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    body = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

    def __str__(self):
        return f"Message from {self.sender} at {self.created_at}"