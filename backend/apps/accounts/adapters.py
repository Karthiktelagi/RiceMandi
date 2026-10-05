"""django-allauth glue for RiceMandi's custom User model.

Google hands us a username and an email — never a phone number, a role, or a
terms agreement. Left alone, allauth would save such a user with
``phone=""`` and the first social sign-up would blow up on the unique index
(``IntegrityError: UNIQUE constraint failed: accounts_user.phone``).

So we do three things here:

1. Default every social user to a *buyer* (merchants need admin approval, and
   we cannot verify a Google identity as a rice trader).
2. Carry over the language the visitor picked before signing in, so a Kannada
   speaker who logs in with Google stays in Kannada.
3. Leave ``phone`` empty and send the user to ``accounts:profile`` afterwards to
   fill it in — see ``ProfileUpdateView``.
"""

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from apps.accounts.models import User


class RiceMandiSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Fill in the custom-user fields that a Google profile cannot provide."""

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        # Google never sends a phone number. ``None`` keeps the unique index
        # happy (SQLite and Postgres both allow repeated NULLs) and marks the
        # profile as incomplete for ``ProfileUpdateView`` to finish.
        if not user.phone:
            user.phone = None

        if not user.role:
            user.role = User.ROLE_BUYER
        if user.role == User.ROLE_MERCHANT:
            # Only an admin can grant the merchant role, so Google users start
            # as buyers. They can request the upgrade from their profile page.
            user.role = User.ROLE_BUYER
        user.is_approved = user.role != User.ROLE_MERCHANT

        # Respect a language chosen via the /lang/<code>/ toggle pre-login.
        session_lang = request.session.get("django_language")
        if session_lang in dict(User.LANG_CHOICES):
            user.preferred_language = session_lang

        return user

    def save_user(self, request, sociallogin, form=None):
        """Safety net: enforce the same defaults if ``populate_user`` was skipped."""
        user = sociallogin.user
        if not user.phone:
            user.phone = None
        if user.role != User.ROLE_MERCHANT:
            user.role = User.ROLE_BUYER
            user.is_approved = True
        return super().save_user(request, sociallogin, form)
