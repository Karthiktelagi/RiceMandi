from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.market import models


@receiver(post_save, sender=models.Lot)
def create_price_record_on_lot_save(sender, instance, created, **kwargs):
    if created:
        models.PriceRecord.objects.create(variety=instance.variety, lot=instance, price_per_quintal=instance.price_per_quintal)
    else:
        last = models.PriceRecord.objects.filter(variety=instance.variety).order_by("-recorded_at").first()
        if last and last.price_per_quintal != instance.price_per_quintal:
            models.PriceRecord.objects.create(variety=instance.variety, lot=instance, price_per_quintal=instance.price_per_quintal)
        elif not last:
            models.PriceRecord.objects.create(variety=instance.variety, lot=instance, price_per_quintal=instance.price_per_quintal)


@receiver(post_save, sender=models.Lot)
def auto_calculate_packet_fields(sender, instance, **kwargs):
    """Auto-calculate packet quantity and price if not provided."""
    if instance.quantity_quintal and not instance.quantity_packets:
        # 1 packet = 26 kg = 0.26 quintal
        instance.quantity_packets = round(instance.quantity_quintal / Decimal("0.26"), 2)
    if instance.price_per_quintal and not instance.price_per_packet:
        instance.price_per_packet = round(instance.price_per_quintal * Decimal("0.26"), 2)
