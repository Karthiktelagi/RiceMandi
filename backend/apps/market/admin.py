from django.contrib import admin

from apps.market.models import Booking, Enquiry, Lot, Mill, Negotiation, PriceRecord, Variety, Watch


@admin.register(Mill)
class MillAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "state", "is_active")
    list_filter = ("is_active", "state")
    search_fields = ("name", "location")


@admin.register(Variety)
class VarietyAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "grade", "is_active", "created_by", "created_at")
    list_filter = ("category", "grade", "is_active")
    search_fields = ("name",)
    readonly_fields = ("created_at",)


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = (
        "variety",
        "merchant",
        "mill",
        "price_per_quintal",
        "quantity_quintal",
        "status",
        "is_available",
        "is_featured",
        "created_at",
    )
    list_filter = ("status", "is_available", "is_featured", "variety__category")
    search_fields = ("variety__name", "merchant__username", "merchant__business_name", "mill__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(PriceRecord)
class PriceRecordAdmin(admin.ModelAdmin):
    list_display = ("variety", "lot", "price_per_quintal", "recorded_at")
    list_filter = ("variety",)
    search_fields = ("variety__name",)
    readonly_fields = ("recorded_at",)


@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display = ("user", "variety", "target_price", "created_at")
    list_filter = ("variety",)
    search_fields = ("user__username", "variety__name")
    readonly_fields = ("created_at",)


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("buyer", "lot", "status", "quantity_wanted", "created_at")
    list_filter = ("status",)
    search_fields = ("buyer__username", "lot__variety__name")
    readonly_fields = ("created_at",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("lot", "buyer", "quantity_quintal", "queue_position", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("lot__variety__name", "buyer__username")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Negotiation)
class NegotiationAdmin(admin.ModelAdmin):
    list_display = ("lot", "buyer", "merchant", "buyer_price", "merchant_price", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("lot__variety__name", "buyer__username", "merchant__username")
    readonly_fields = ("created_at", "updated_at")
