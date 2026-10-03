"""
Management command to check active PriceAlerts against current lot prices.

When a lot's price_per_quintal drops to or below a user's target_price,
the alert is marked triggered and a Notification is created.

Run via: python manage.py check_price_alerts
Schedule with cron or a task scheduler (e.g. Render Cron Job).
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Min
from django.utils.translation import gettext_lazy as _

from apps.market.models import Lot, PriceAlert
from apps.notifications.models import Notification


class Command(BaseCommand):
    help = _("Check price alerts and notify users when target prices are reached.")

    def handle(self, *args, **options):
        # Get all active, untriggered alerts
        alerts = PriceAlert.objects.filter(is_active=True, triggered=False).select_related("user", "variety")

        if not alerts.exists():
            self.stdout.write(self.style.SUCCESS(_("No active price alerts to check.")))
            return

        triggered_count = 0
        notification_count = 0

        for alert in alerts:
            # Find the lowest current price for this variety
            lowest_price = (
                Lot.objects.filter(
                    variety=alert.variety,
                    status=Lot.STATUS_ACTIVE,
                    is_available=True,
                )
                .aggregate(min_price=Min("price_per_quintal"))
                .get("min_price")
            )

            if lowest_price is None:
                continue

            if lowest_price <= alert.target_price:
                # Mark alert as triggered
                alert.triggered = True
                alert.save(update_fields=["triggered"])
                triggered_count += 1

                # Create notification
                Notification.objects.create(
                    recipient=alert.user,
                    kind=Notification.KIND_PRICE_DROP,
                    title=_("Price Alert: %(variety)s") % {"variety": alert.variety.name},
                    body=_(
                        "The price for %(variety)s has dropped to ₹%(price)/quintal or below your target of ₹%(target)/quintal."
                    )
                    % {
                        "variety": alert.variety.name,
                        "price": lowest_price,
                        "target": alert.target_price,
                    },
                    url=f"/varieties/{alert.variety.pk}/",
                )
                notification_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                _("Checked %(alerts)d alerts: %(triggered)d triggered, %(notified)d notifications created.")
                % {
                    "alerts": alerts.count(),
                    "triggered": triggered_count,
                    "notified": notification_count,
                }
            )
        )
