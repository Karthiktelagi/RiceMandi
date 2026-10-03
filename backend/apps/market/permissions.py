from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied


def is_admin(user):
    return user.is_authenticated and user.role == user.ROLE_ADMIN


def is_merchant(user):
    return user.is_authenticated and user.role == user.ROLE_MERCHANT


def is_approved_merchant(user):
    return is_merchant(user) and user.is_approved


def is_buyer_or_merchant(user):
    return user.is_authenticated and user.role in (user.ROLE_BUYER, user.ROLE_MERCHANT, user.ROLE_ADMIN)


def merchant_required(view_func):
    return login_required(user_passes_test(lambda u: is_merchant(u) or u.is_superuser)(view_func))


def approved_merchant_required(view_func):
    return login_required(user_passes_test(lambda u: is_approved_merchant(u) or u.is_superuser)(view_func))


def admin_required(view_func):
    return login_required(user_passes_test(lambda u: is_admin(u) or u.is_superuser)(view_func))
