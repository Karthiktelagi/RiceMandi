from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLE_BUYER = "buyer"
    ROLE_MERCHANT = "merchant"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = (
        (ROLE_BUYER, _("Buyer")),
        (ROLE_MERCHANT, _("Merchant")),
        (ROLE_ADMIN, _("Admin")),
    )

    LANG_KANNADA = "kn"
    LANG_ENGLISH = "en"
    LANG_CHOICES = (
        (LANG_KANNADA, _("Kannada")),
        (LANG_ENGLISH, _("English")),
    )

    phone = models.CharField(max_length=15, unique=True, db_index=True)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_BUYER)
    is_approved = models.BooleanField(default=True, help_text=_("Merchants require admin approval"))
    business_name = models.CharField(max_length=150, blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    preferred_language = models.CharField(max_length=2, choices=LANG_CHOICES, default=LANG_ENGLISH)

    def __str__(self):
        if self.role == self.ROLE_MERCHANT and self.business_name:
            return self.business_name
        return self.get_username()

    class Meta:
        db_table = "accounts_user"
        ordering = ["username"]
