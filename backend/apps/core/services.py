from decimal import Decimal

from django.db.models import Avg, Count, Max, Min, Q

from apps.market.models import Lot, Variety


KG_PER_QUINTAL = 100
KG_PER_PACKET = 26


def calculate_packet_price(price_per_quintal):
    if price_per_quintal is None:
        return None
    return round(price_per_quintal / Decimal(KG_PER_QUINTAL) * Decimal(KG_PER_PACKET))


def get_rate_board_varieties():
    return (
        Variety.objects.filter(is_active=True)
        .annotate(
            min_price=Min("lots__price_per_quintal", filter=Q(lots__status=Lot.STATUS_ACTIVE, lots__is_available=True)),
            max_price=Max("lots__price_per_quintal", filter=Q(lots__status=Lot.STATUS_ACTIVE, lots__is_available=True)),
            avg_price=Avg("lots__price_per_quintal", filter=Q(lots__status=Lot.STATUS_ACTIVE, lots__is_available=True)),
            lot_count=Count("lots", filter=Q(lots__status=Lot.STATUS_ACTIVE, lots__is_available=True)),
        )
        .filter(lot_count__gt=0)
        .order_by("name")
    )
