from rest_framework import serializers

from apps.market.models import Lot, Mill, Variety


class VarietySerializer(serializers.ModelSerializer):
    class Meta:
        model = Variety
        fields = ("id", "name", "category", "grade", "is_active")


class MillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mill
        fields = ("id", "name", "location", "state", "is_active")


class LotSerializer(serializers.ModelSerializer):
    variety_name = serializers.CharField(source="variety.name", read_only=True)
    mill_name = serializers.CharField(source="mill.name", read_only=True)
    merchant_name = serializers.CharField(source="merchant.business_name", read_only=True)

    class Meta:
        model = Lot
        fields = (
            "id",
            "variety",
            "variety_name",
            "mill",
            "mill_name",
            "merchant",
            "merchant_name",
            "price_per_quintal",
            "quantity_quintal",
            "moisture_pct",
            "broken_pct",
            "status",
            "is_available",
            "is_featured",
            "created_at",
        )
