from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.notifications.models import Notification

User = get_user_model()


class NotificationViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="notify_user",
            password="password123",
            role=User.ROLE_BUYER,
        )
        self.other_user = User.objects.create_user(
            username="other_user",
            password="password123",
            role=User.ROLE_BUYER,
        )
        self.notif1 = Notification.objects.create(
            recipient=self.user,
            kind=Notification.KIND_PRICE_DROP,
            title="Price Drop Alert",
            body="Variety price dropped!",
            url="/varieties/",
            is_read=False,
        )
        self.notif2 = Notification.objects.create(
            recipient=self.user,
            kind=Notification.KIND_ENQUIRY,
            title="New Enquiry",
            body="Someone enquired about your lot",
            is_read=False,
        )

    def test_notification_list(self):
        """User can view their notifications."""
        self.client.login(username="notify_user", password="password123")
        url = reverse("notifications:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["unread_count"], 2)

    def test_notification_mark_read(self):
        """Marking a notification as read updates its status and redirects to target url."""
        self.client.login(username="notify_user", password="password123")
        url = reverse("notifications:mark_read", args=[self.notif1.pk])
        response = self.client.get(url)
        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.is_read)
        self.assertRedirects(response, "/varieties/")

    def test_notification_mark_all_read(self):
        """Marking all as read updates all unread notifications."""
        self.client.login(username="notify_user", password="password123")
        url = reverse("notifications:mark_all_read")
        response = self.client.get(url)
        self.assertRedirects(response, reverse("notifications:list"))
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 0)

    def test_user_cannot_mark_other_user_notification(self):
        """User cannot mark another user's notification as read."""
        self.client.login(username="other_user", password="password123")
        url = reverse("notifications:mark_read", args=[self.notif1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
