from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def lot_photo_upload(instance, filename):
    return f"lots/{instance.pk or 'new'}/{filename}"


def variety_photo_upload(instance, filename):
    return f"varieties/{instance.pk or 'new'}/{filename}"


class Mill(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    location = models.CharField(max_length=150)
    state = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15, blank=True)
    capacity_quintal_per_day = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Mill")
        verbose_name_plural = _("Mills")

    def __str__(self):
        return self.name


class Variety(models.Model):
    CATEGORY_PADDY = "paddy"
    CATEGORY_RICE = "rice"
    CATEGORY_BROKEN = "broken"
    CATEGORY_BRAN = "bran"
    CATEGORY_CHOICES = (
        (CATEGORY_PADDY, _("Paddy")),
        (CATEGORY_RICE, _("Rice")),
        (CATEGORY_BROKEN, _("Broken")),
        (CATEGORY_BRAN, _("Bran")),
    )

    GRADE_G1 = "grade_1"
    GRADE_G2 = "grade_2"
    GRADE_COMMON = "common"
    GRADE_CHOICES = (
        (GRADE_G1, _("Grade 1")),
        (GRADE_G2, _("Grade 2")),
        (GRADE_COMMON, _("Common")),
    )

    name = models.CharField(max_length=120, db_index=True)
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES)
    grade = models.CharField(max_length=16, choices=GRADE_CHOICES, default=GRADE_COMMON)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=variety_photo_upload, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_varieties"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Variety")
        verbose_name_plural = _("Varieties")

    def clean(self):
        super().clean()
        if self.name:
            trimmed = self.name.strip()
            if trimmed != self.name:
                self.name = trimmed
            qs = Variety.objects.filter(name__iexact=trimmed)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                existing = qs.first()
                raise ValidationError(
                    {
                        "name": _(
                            'The variety "%(name)s" already exists. Use the existing variety instead.'
                        )
                        % {"name": trimmed}
                    }
                )

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Lot(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_SOLD = "sold"
    STATUS_WITHDRAWN = "withdrawn"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, _("Active")),
        (STATUS_SOLD, _("Sold")),
        (STATUS_WITHDRAWN, _("Withdrawn")),
    )

    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lots"
    )
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE, related_name="lots")
    mill = models.ForeignKey(Mill, on_delete=models.CASCADE, related_name="lots")
    price_per_quintal = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_quintal = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_packets = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Packets (1 packet = 26 kg)")
    price_per_packet = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Rate per packet (₹ per 26 kg)")
    demand = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Demand in quintals")
    available_quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Available quantity")
    arrival_date = models.DateField()
    moisture_pct = models.DecimalField(max_digits=5, decimal_places=2)
    broken_pct = models.DecimalField(max_digits=5, decimal_places=2)
    grain_length_mm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    milling_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to=lot_photo_upload, blank=True, null=True)
    is_available = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Lot")
        verbose_name_plural = _("Lots")

    def __str__(self):
        return f"{self.variety} - ₹{self.price_per_quintal}/q"


class PriceRecord(models.Model):
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE, related_name="price_records")
    lot = models.ForeignKey(Lot, on_delete=models.SET_NULL, null=True, blank=True, related_name="price_records")
    price_per_quintal = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-recorded_at"]
        verbose_name = _("Price Record")
        verbose_name_plural = _("Price Records")

    def __str__(self):
        return f"{self.variety} @ {self.price_per_quintal} on {self.recorded_at}"


class Watch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watches")
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE, related_name="watches")
    target_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "variety")
        ordering = ["-created_at"]
        verbose_name = _("Watch")
        verbose_name_plural = _("Watches")

    def __str__(self):
        return f"{self.user} watching {self.variety}"


class Enquiry(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = (
        (STATUS_OPEN, _("Open")),
        (STATUS_CLOSED, _("Closed")),
    )

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enquiries_made")
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="enquiries")
    message = models.TextField()
    quantity_wanted = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Enquiry")
        verbose_name_plural = _("Enquiries")

    def __str__(self):
        return f"Enquiry by {self.buyer} for {self.lot}"


class Booking(models.Model):
    """First-come-first-serve queue for lots."""
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_CONFIRMED, _("Confirmed")),
        (STATUS_CANCELLED, _("Cancelled")),
        (STATUS_COMPLETED, _("Completed")),
    )

    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="bookings")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    quantity_quintal = models.DecimalField(max_digits=10, decimal_places=2)
    queue_position = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["queue_position", "created_at"]
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")
        unique_together = ("lot", "buyer")

    def __str__(self):
        return f"#{self.queue_position} {self.buyer} -> {self.lot}"


class Negotiation(models.Model):
    """Price negotiation between buyer and merchant on a lot."""
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_COUNTERED = "countered"
    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_ACCEPTED, _("Accepted")),
        (STATUS_REJECTED, _("Rejected")),
        (STATUS_COUNTERED, _("Countered")),
    )

    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="negotiations")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="negotiations_made")
    merchant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="negotiations_received")
    buyer_price = models.DecimalField(max_digits=10, decimal_places=2)
    merchant_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity_quintal = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Negotiation")
        verbose_name_plural = _("Negotiations")

    def __str__(self):
        return f"Negotiation on {self.lot}: ₹{self.buyer_price} vs ₹{self.merchant_price or '—'}"


class PriceAlert(models.Model):
    """Price drop alerts - like Bijak, Kisan Setra."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="price_alerts")
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE, related_name="price_alerts")
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "variety", "target_price")
        ordering = ["-created_at"]
        verbose_name = _("Price Alert")
        verbose_name_plural = _("Price Alerts")

    def __str__(self):
        return f"{self.user} alert {self.variety} @ ₹{self.target_price}"


class TraderRating(models.Model):
    """Rating system - like Bijak."""
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings_given")
    rated = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings_received")
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, null=True, blank=True, related_name="ratings")
    rating = models.PositiveSmallIntegerField(choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("rater", "rated", "lot")
        ordering = ["-created_at"]
        verbose_name = _("Trader Rating")
        verbose_name_plural = _("Trader Ratings")

    def __str__(self):
        return f"{self.rater} rated {self.rated} {self.rating}/5"


class MarketTrend(models.Model):
    """Daily market price trends - like agriSATHI, Khoj."""
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE, related_name="trends")
    date = models.DateField(db_index=True)
    avg_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume_quintal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("variety", "date")
        ordering = ["-date"]
        verbose_name = _("Market Trend")
        verbose_name_plural = _("Market Trends")

    def __str__(self):
        return f"{self.variety} on {self.date}: ₹{self.avg_price}"
