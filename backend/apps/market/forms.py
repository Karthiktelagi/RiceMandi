from django import forms
from django.utils.translation import gettext_lazy as _

from apps.market.models import Lot, Mill, Variety


class VarietyForm(forms.ModelForm):
    class Meta:
        model = Variety
        fields = ("name", "category", "grade", "description", "image")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "grade": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        if name:
            name = name.strip()
        return name


class LotForm(forms.ModelForm):
    class Meta:
        model = Lot
        fields = (
            "variety",
            "mill",
            "price_per_quintal",
            "quantity_quintal",
            "quantity_packets",
            "price_per_packet",
            "demand",
            "available_quantity",
            "arrival_date",
            "moisture_pct",
            "broken_pct",
            "grain_length_mm",
            "milling_pct",
            "notes",
            "photo",
            "is_available",
        )
        widgets = {
            "variety": forms.Select(attrs={"class": "form-select"}),
            "mill": forms.Select(attrs={"class": "form-select"}),
            "price_per_quintal": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "quantity_quintal": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "quantity_packets": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "price_per_packet": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "demand": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "available_quantity": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "arrival_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "moisture_pct": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "broken_pct": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "grain_length_mm": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "milling_pct": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class MillForm(forms.ModelForm):
    class Meta:
        model = Mill
        fields = ("name", "location", "state", "contact_phone", "capacity_quintal_per_day", "is_active")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-control"}),
            "capacity_quintal_per_day": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
