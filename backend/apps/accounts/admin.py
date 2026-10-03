from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            _("RiceMandi"),
            {
                "fields": (
                    "phone",
                    "role",
                    "is_approved",
                    "business_name",
                    "gst_number",
                    "photo",
                    "preferred_language",
                )
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            _("RiceMandi"),
            {
                "fields": (
                    "phone",
                    "role",
                    "is_approved",
                    "business_name",
                    "gst_number",
                    "preferred_language",
                )
            },
        ),
    )
    list_display = ("username", "email", "phone", "role", "is_approved", "is_staff", "is_active")
    list_filter = ("role", "is_approved", "is_staff", "is_active")
    search_fields = ("username", "email", "phone", "business_name")
