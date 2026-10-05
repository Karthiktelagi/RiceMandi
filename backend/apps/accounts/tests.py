"""Tests for the auth flows.

The Google cases drive allauth's *real* pipeline
(``sociallogin_from_response`` -> ``complete_social_login``) and only skip the
HTTP token exchange with Google, so the adapter, the unique phone index and the
database writes are genuinely exercised.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from allauth.core import context
from allauth.socialaccount.adapter import get_adapter as get_social_adapter
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialAccount, SocialToken
from allauth.socialaccount.providers.google.provider import GoogleProvider

User = get_user_model()

GOOGLE_PROFILE = {
    "id": "112233445566778899000",
    "email": "asha.rao@example.com",
    "verified_email": True,
    "name": "Asha Rao",
    "given_name": "Asha",
    "family_name": "Rao",
}


def fake_request(language=None):
    """A request with the middleware allauth's pipeline expects, no HTTP."""
    request = RequestFactory().get("/accounts/google/login/callback/")
    SessionMiddleware(lambda r: None).process_request(request)
    AuthenticationMiddleware(lambda r: None).process_request(request)
    MessageMiddleware(lambda r: None).process_request(request)
    if language:
        request.session["django_language"] = language
    return request


def do_google_login(profile=None, language=None):
    """Run the full allauth Google login pipeline for a synthetic profile.

    ``request_context`` is what ``AccountMiddleware`` normally provides: it is
    how allauth's ``get_adapter()`` finds the current request. Only the HTTP
    token exchange with Google is skipped.
    """
    profile = profile or GOOGLE_PROFILE
    request = fake_request(language)
    request.allauth = SimpleNamespace()

    with context.request_context(request):
        app = get_social_adapter().get_app(request, "google")
        sociallogin = GoogleProvider(request, app).sociallogin_from_response(
            request, dict(profile)
        )
        complete_social_login(request, sociallogin)

    return request


class GoogleSignInTests(TestCase):
    """"Continue with Google" must create a usable database record."""

    def test_google_login_writes_user_and_social_rows(self):
        do_google_login()

        user = User.objects.get(email=GOOGLE_PROFILE["email"])
        self.assertTrue(user.username)
        self.assertIsNone(user.phone)           # collected on accounts:profile
        self.assertEqual(user.role, User.ROLE_BUYER)
        self.assertTrue(user.is_approved)
        self.assertFalse(user.has_usable_password())

        social = SocialAccount.objects.get(provider="google", user=user)
        self.assertEqual(social.uid, GOOGLE_PROFILE["id"])
        self.assertEqual(social.extra_data["email"], GOOGLE_PROFILE["email"])

    def test_google_login_stores_no_oauth_token(self):
        """We only use Google to prove identity, so tokens are not retained."""
        do_google_login()
        self.assertEqual(SocialToken.objects.count(), 0)

    def test_two_google_users_do_not_clash_on_unique_phone(self):
        """Regression: phone is unique, and every social user leaves it NULL."""
        do_google_login()
        do_google_login({
            "id": "998877665544332211000",
            "email": "ravi.kumar@example.com",
            "verified_email": True,
            "name": "Ravi Kumar",
            "given_name": "Ravi",
            "family_name": "Kumar",
        })

        self.assertEqual(User.objects.filter(email__endswith="@example.com").count(), 2)
        self.assertEqual(
            User.objects.filter(email__endswith="@example.com", phone__isnull=True).count(),
            2,
        )

    def test_google_login_cannot_self_assign_merchant_role(self):
        do_google_login()
        self.assertEqual(User.objects.get(email=GOOGLE_PROFILE["email"]).role, User.ROLE_BUYER)

    def test_google_login_keeps_pre_login_language_choice(self):
        do_google_login(language="kn")
        self.assertEqual(User.objects.get(email=GOOGLE_PROFILE["email"]).preferred_language, "kn")


class ProfileCompletionTests(TestCase):
    """A Google user lands on accounts:profile to supply phone + role."""

    def setUp(self):
        do_google_login()
        self.user = User.objects.get(email=GOOGLE_PROFILE["email"])

    def test_profile_page_is_shown_when_phone_is_missing(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_profile_page_is_skipped_once_complete(self):
        self.user.phone = "9876543210"
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertRedirects(response, reverse("accounts:dashboard"))

    def test_staff_is_not_held_up_by_the_profile_gate(self):
        staff = User.objects.create_superuser(
            username="boss", password="Str0ng-Pass-99!", email="boss@example.com"
        )
        self.assertIsNone(staff.phone)
        self.client.force_login(staff)
        response = self.client.get(reverse("accounts:profile"))
        self.assertRedirects(response, reverse("accounts:dashboard"))

    def test_saving_profile_stores_phone_and_flips_merchant_to_unapproved(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:profile"), {
            "phone": "9876543210",
            "role": User.ROLE_MERCHANT,
            "business_name": "Asha Rice Traders",
            "gst_number": "29ABCDE1234F1Z5",
        })
        self.assertRedirects(response, reverse("accounts:dashboard"))

        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "9876543210")
        self.assertEqual(self.user.role, User.ROLE_MERCHANT)
        self.assertFalse(self.user.is_approved)

    def test_merchant_without_business_name_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:profile"), {
            "phone": "9876543210",
            "role": User.ROLE_MERCHANT,
            "business_name": "",
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.phone)

    def test_duplicate_phone_is_rejected(self):
        User.objects.create_user(
            username="existing", password="Str0ng-Pass-99!", phone="9876543210"
        )
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:profile"), {
            "phone": "9876543210",
            "role": User.ROLE_BUYER,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "phone", "This phone number is already registered"
        )


class GoogleCallbackTests(TestCase):
    """Drive the real /accounts/google/login/callback/ URL.

    Only Google's HTTP responses are faked. This is the regression test for the
    HTTP 500 users hit after approving the Google consent screen:
    ``ModuleNotFoundError: No module named 'jwt'``. Google echoes an ``id_token``
    back because the scope includes ``openid``, and allauth decodes it with
    PyJWT, so a missing PyJWT took the whole callback down.
    """

    def _google_auth(self):
        """Walk the real redirect to Google, then hit the callback URL."""
        with mock.patch(
            "allauth.socialaccount.providers.oauth2.client.OAuth2Client.get_access_token",
            return_value={
                "access_token": "ya29.test-access-token",
                "token_type": "Bearer",
                "expires_in": 3599,
                # Present in a real Google response; drives the id_token path.
                "id_token": "header.payload.signature",
            },
        ), mock.patch(
            # Decoding the signature would need Google's real certs.
            "allauth.socialaccount.providers.google.views._verify_and_decode",
            return_value=dict(GOOGLE_PROFILE),
        ), mock.patch(
            "allauth.socialaccount.providers.google.views."
            "GoogleOAuth2Adapter._fetch_user_info",
            return_value=dict(GOOGLE_PROFILE),
        ):
            start = self.client.get(reverse("google_login"))
            self.assertEqual(start.status_code, 302, "should redirect to Google")

            state = dict(
                pair.split("=", 1) for pair in start["Location"].split("?", 1)[1].split("&")
            )["state"]
            # allauth does not give the callback a reversible url name, so
            # derive it: /accounts/google/login/ -> .../login/callback/
            callback = f"{reverse('google_login')}callback/"
            return self.client.get(
                callback,
                {"code": "4/0AXfake", "state": state, "scope": "email profile openid"},
            )

    def test_callback_signs_the_user_in_and_persists_the_record(self):
        response = self._google_auth()

        self.assertEqual(response.status_code, 302, getattr(response, "content", b"")[:400])
        self.assertEqual(response["Location"], reverse("accounts:profile"))

        user = User.objects.get(email=GOOGLE_PROFILE["email"])
        self.assertIsNone(user.phone)
        self.assertEqual(user.role, User.ROLE_BUYER)
        self.assertTrue(SocialAccount.objects.filter(user=user, provider="google").exists())

    def test_id_token_decoding_dependency_is_importable(self):
        """Guards the requirements.txt entry that caused the 500."""
        import jwt  # noqa: F401

    def test_requirements_lists_every_allauth_dependency(self):
        """A missing line here means a broken deploy, not just local pain."""
        reqs = (Path(__file__).resolve().parents[2] / "requirements.txt").read_text().lower()
        for package in ("django-allauth", "requests", "pyjwt"):
            with self.subTest(package=package):
                self.assertIn(package, reqs)


class SignUpTests(TestCase):
    """The local sign-up form: terms gate, persistence, merchant approval."""

    payload = {
        "username": "buyer1",
        "email": "buyer1@example.com",
        "phone": "9812345678",
        "role": User.ROLE_BUYER,
        "password1": "Str0ng-Pass-99!",
        "password2": "Str0ng-Pass-99!",
    }

    def test_signup_requires_agreement_to_terms(self):
        response = self.client.post(reverse("accounts:signup"), self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="buyer1").exists())
        self.assertFormError(
            response.context["form"], "terms",
            "You must agree to the Terms of Service and Privacy Policy",
        )

    def test_signup_creates_buyer_and_forwards_to_login(self):
        response = self.client.post(
            reverse("accounts:signup"), {**self.payload, "terms": "on"}
        )
        self.assertRedirects(response, reverse("accounts:login"))

        user = User.objects.get(username="buyer1")
        self.assertEqual(user.email, "buyer1@example.com")
        self.assertEqual(user.phone, "9812345678")
        self.assertEqual(user.role, User.ROLE_BUYER)
        self.assertTrue(user.is_approved)

    def test_signup_creates_unapproved_merchant(self):
        response = self.client.post(reverse("accounts:signup"), {
            **self.payload,
            "role": User.ROLE_MERCHANT,
            "business_name": "Ravi Rice Mills",
            "terms": "on",
        })
        self.assertRedirects(response, reverse("accounts:login"))

        user = User.objects.get(username="buyer1")
        self.assertEqual(user.role, User.ROLE_MERCHANT)
        self.assertFalse(user.is_approved)
        self.assertEqual(user.business_name, "Ravi Rice Mills")

    def test_duplicate_phone_is_rejected(self):
        User.objects.create_user(
            username="taken", password="Str0ng-Pass-99!", phone="9812345678"
        )
        response = self.client.post(
            reverse("accounts:signup"), {**self.payload, "terms": "on"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "phone", "This phone number is already registered"
        )


class LegalPagesTests(TestCase):
    def test_terms_and_privacy_render(self):
        for name in ("core:terms", "core:privacy"):
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
