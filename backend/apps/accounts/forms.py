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
    terms = forms.BooleanField(
        required=True,
        label=_("I agree to the Terms of Service and Privacy Policy"),
        error_messages={"required": _("You must agree to the Terms of Service and Privacy Policy")},
    )

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


class ProfileForm(forms.ModelForm):
    """Finishes the record for users created by Google sign-in.

    Google supplies a username and email but never a phone number, so
    ``User.phone`` is left NULL and we collect it here on first login.
    """

    class Meta:
        model = User
        fields = ("phone", "role", "business_name", "gst_number")
        widgets = {
            "phone": forms.TextInput(attrs={"placeholder": _("Enter your phone number")}),
            "business_name": forms.TextInput(attrs={"placeholder": _("Your business name")}),
            "gst_number": forms.TextInput(attrs={"placeholder": _("GST number (optional)")}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].label = _("Phone number")
        self.fields["role"].label = _("I am a")
        self.fields["role"].choices = [
            (User.ROLE_BUYER, _("Buyer")),
            (User.ROLE_MERCHANT, _("Merchant")),
        ]
        # A merchant must give a business name, a buyer has no use for one.
        self.fields["business_name"].required = False

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if phone:
            clash = User.objects.filter(phone=phone)
            if self.instance.pk:
                clash = clash.exclude(pk=self.instance.pk)
            if clash.exists():
                raise forms.ValidationError(_("This phone number is already registered"))
        return phone or None

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("role") == User.ROLE_MERCHANT and not (cleaned.get("business_name") or "").strip():
            self.add_error("business_name", _("Merchants must provide a business name"))
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        if user.role == User.ROLE_MERCHANT:
            user.is_approved = False
        else:
            user.is_approved = True
            user.business_name = ""
            user.gst_number = ""
        if commit:
            user.save()
        return user
