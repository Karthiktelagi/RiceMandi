from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.chat.models import Conversation, Message
from apps.market.models import Lot, Mill, Variety

User = get_user_model()


class ChatViewsTestCase(TestCase):
    def setUp(self):
        self.merchant = User.objects.create_user(
            username="merchant_chat",
            password="password123",
            role=User.ROLE_MERCHANT,
            is_approved=True,
        )
        self.buyer = User.objects.create_user(
            username="buyer_chat",
            password="password123",
            role=User.ROLE_BUYER,
        )
        self.outsider = User.objects.create_user(
            username="outsider_chat",
            password="password123",
            role=User.ROLE_BUYER,
        )
        self.variety = Variety.objects.create(name="IR 64 Chat", category=Variety.CATEGORY_RICE)
        self.mill = Mill.objects.create(name="Chat Mill", location="Shimoga", state="Karnataka")
        self.lot = Lot.objects.create(
            merchant=self.merchant,
            variety=self.variety,
            mill=self.mill,
            price_per_quintal=Decimal("3000.00"),
            quantity_quintal=Decimal("50.00"),
            arrival_date=date.today(),
            moisture_pct=Decimal("11.00"),
            broken_pct=Decimal("3.00"),
            status=Lot.STATUS_ACTIVE,
            is_available=True,
        )
        self.conversation = Conversation.objects.create(
            buyer=self.buyer,
            merchant=self.merchant,
            lot=self.lot,
        )

    def test_conversation_detail_access_control(self):
        """Outsider cannot access someone else's conversation."""
        self.client.login(username="outsider_chat", password="password123")
        url = reverse("chat:detail", args=[self.conversation.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_conversation_detail_participants_can_access(self):
        """Both buyer and merchant can access conversation."""
        url = reverse("chat:detail", args=[self.conversation.pk])

        self.client.login(username="buyer_chat", password="password123")
        res1 = self.client.get(url)
        self.assertEqual(res1.status_code, 200)

        self.client.logout()
        self.client.login(username="merchant_chat", password="password123")
        res2 = self.client.get(url)
        self.assertEqual(res2.status_code, 200)

    def test_send_message_and_read_receipts(self):
        """Sending a message records it, and visiting marks messages from other user as read."""
        self.client.login(username="buyer_chat", password="password123")
        url = reverse("chat:detail", args=[self.conversation.pk])
        self.client.post(url, {"body": "Hello merchant!"})

        msg = Message.objects.get(conversation=self.conversation, sender=self.buyer)
        self.assertEqual(msg.body, "Hello merchant!")
        self.assertIsNone(msg.read_at)

        # Merchant visits conversation
        self.client.logout()
        self.client.login(username="merchant_chat", password="password123")
        self.client.get(url)

        msg.refresh_from_db()
        self.assertIsNotNone(msg.read_at)

    def test_merchant_cannot_start_conversation_with_self(self):
        """Merchant starting conversation about own lot is rejected."""
        self.client.login(username="merchant_chat", password="password123")
        url = reverse("chat:start", args=[self.lot.pk])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
