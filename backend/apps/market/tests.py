from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.chat.models import Conversation
from apps.market.models import Booking, Lot, Mill, Negotiation, Variety, Watch
from apps.notifications.models import Notification

User = get_user_model()


class MarketViewsTestCase(TestCase):
    def setUp(self):
        self.merchant = User.objects.create_user(
            username="merchant_test",
            password="password123",
            role=User.ROLE_MERCHANT,
            is_approved=True,
        )
        self.buyer1 = User.objects.create_user(
            username="buyer1_test",
            password="password123",
            role=User.ROLE_BUYER,
        )
        self.buyer2 = User.objects.create_user(
            username="buyer2_test",
            password="password123",
            role=User.ROLE_BUYER,
        )
        self.variety = Variety.objects.create(
            name="Sona Masoori Test",
            category=Variety.CATEGORY_RICE,
            grade=Variety.GRADE_COMMON,
        )
        self.mill = Mill.objects.create(
            name="Test Rice Mill",
            location="Raichur",
            state="Karnataka",
        )
        self.lot = Lot.objects.create(
            merchant=self.merchant,
            variety=self.variety,
            mill=self.mill,
            price_per_quintal=Decimal("3500.00"),
            quantity_quintal=Decimal("100.00"),
            arrival_date=date.today(),
            moisture_pct=Decimal("12.50"),
            broken_pct=Decimal("4.00"),
            status=Lot.STATUS_ACTIVE,
            is_available=True,
        )

    def test_watch_toggle_post_only(self):
        """watch_toggle must reject GET requests with 405 Method Not Allowed."""
        self.client.login(username="buyer1_test", password="password123")
        url = reverse("market:watch_toggle", args=[self.variety.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_watch_toggle_success(self):
        """POST toggles watch on and off."""
        self.client.login(username="buyer1_test", password="password123")
        url = reverse("market:watch_toggle", args=[self.variety.pk])
        
        # Turn watch ON
        res1 = self.client.post(url, follow=True)
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(Watch.objects.filter(user=self.buyer1, variety=self.variety).exists())

        # Turn watch OFF
        res2 = self.client.post(url, follow=True)
        self.assertEqual(res2.status_code, 200)
        self.assertFalse(Watch.objects.filter(user=self.buyer1, variety=self.variety).exists())

    def test_book_lot_post_only(self):
        """book_lot must reject GET requests with 405."""
        self.client.login(username="buyer1_test", password="password123")
        url = reverse("market:book_lot", args=[self.lot.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_book_lot_merchant_cannot_book_own_lot(self):
        """Merchant is prevented from booking their own lot."""
        self.client.login(username="merchant_test", password="password123")
        url = reverse("market:book_lot", args=[self.lot.pk])
        response = self.client.post(url, {"quantity_quintal": "10"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Booking.objects.filter(lot=self.lot, buyer=self.merchant).exists())

    def test_book_lot_queue_ordering(self):
        """First-come-first-serve queue positions increment sequentially."""
        # Buyer 1 books
        self.client.login(username="buyer1_test", password="password123")
        url = reverse("market:book_lot", args=[self.lot.pk])
        self.client.post(url, {"quantity_quintal": "20"})
        b1 = Booking.objects.get(lot=self.lot, buyer=self.buyer1)
        self.assertEqual(b1.queue_position, 1)

        # Buyer 2 books
        self.client.logout()
        self.client.login(username="buyer2_test", password="password123")
        self.client.post(url, {"quantity_quintal": "30"})
        b2 = Booking.objects.get(lot=self.lot, buyer=self.buyer2)
        self.assertEqual(b2.queue_position, 2)

    def test_negotiate_lot_merchant_cannot_negotiate_own_lot(self):
        """Merchant cannot send negotiation offers on their own lot."""
        self.client.login(username="merchant_test", password="password123")
        url = reverse("market:negotiate_lot", args=[self.lot.pk])
        response = self.client.post(url, {"buyer_price": "3400", "quantity_quintal": "10"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Negotiation.objects.filter(lot=self.lot, buyer=self.merchant).exists())

    def test_negotiate_lot_buyer_success(self):
        """Buyer successfully sends negotiation offer."""
        self.client.login(username="buyer1_test", password="password123")
        url = reverse("market:negotiate_lot", args=[self.lot.pk])
        response = self.client.post(url, {"buyer_price": "3400", "quantity_quintal": "10", "message": "Best rate"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Negotiation.objects.filter(lot=self.lot, buyer=self.buyer1, buyer_price=Decimal("3400")).exists())

    def test_enquire_lot_creates_conversation_and_notification(self):
        """Enquiring creates an enquiry record, chat conversation, and notification for the merchant."""
        self.client.login(username="buyer1_test", password="password123")
        url = reverse("market:enquire_lot", args=[self.lot.pk])
        response = self.client.post(url, {"message": "Is this still available?", "quantity_wanted": "50"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Conversation.objects.filter(buyer=self.buyer1, merchant=self.merchant, lot=self.lot).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.merchant, kind=Notification.KIND_ENQUIRY).exists())
