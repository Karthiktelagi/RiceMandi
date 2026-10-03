from django.contrib import admin

from apps.chat.models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("buyer", "merchant", "lot", "created_at", "last_message_at")
    search_fields = ("buyer__username", "merchant__username", "merchant__business_name")
    readonly_fields = ("created_at", "last_message_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "created_at", "read_at")
    search_fields = ("body", "sender__username")
    readonly_fields = ("created_at",)
