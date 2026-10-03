from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class SignUpForm(UserCreationForm):
    phone = forms.CharField(max_length=15, label=_("Phone number"))
    role = forms.ChoiceField(
        choices=[(User.ROLE_BUYER, _("Buyer")), (User.ROLE_MERCHANT, _("Merchant"))],
        label=_("I am a"),
    )
    business_name = forms.CharField(max_length=150, required=False, label=_("Business name"))
    gst_number = forms.CharField(max_length=20, required=False, label=_("GST number"))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "phone",
            "role",
            "business_name",
            "gst_number",
            "password1",
            "password2",
        )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            raise forms.ValidationError(_("Phone number is required"))
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError(_("This phone number is already registered"))
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data["phone"]
        user.role = self.cleaned_data["role"]
        if user.role == User.ROLE_MERCHANT:
            user.is_approved = False
            user.business_name = self.cleaned_data.get("business_name", "")
            user.gst_number = self.cleaned_data.get("gst_number", "")
        else:
            user.is_approved = True
            user.business_name = ""
            user.gst_number = ""
        if commit:
            user.save()
        return user
