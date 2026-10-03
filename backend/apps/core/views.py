from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max, Min, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import translation
from django.views.decorators.http import require_GET

from apps.accounts.utils import safe_redirect

LANGUAGE_CODES = ("kn", "en")


@require_GET
def set_language(request, code):
    """Set the active language, persist the choice, return the user to where
    they came from.

    The navbar toggle is a plain link so it works without JavaScript. A POST
    form would be stricter, but switching a display language is not a state
    change worth CSRF-protecting.
    """
    if code not in LANGUAGE_CODES:
        code = "en"

    translation.activate(code)
    request.session["django_language"] = code

    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        # Remember the choice on the account so a new device still starts in
        # the right language.
        user.preferred_language = code
        user.save(update_fields=["preferred_language"])

    return HttpResponseRedirect(safe_redirect(request.GET.get("next"), reverse("core:home")))


@login_required
def dashboard(request):
    """Role-aware dashboard. Milestone 3 gives each role its own content."""
    return render(request, "accounts/dashboard.html")


def home(request):
    """Home page - Rate board showing live rates per variety."""
    from django.db.models import Avg, Max, Min, Q

    from apps.accounts.models import User
    from apps.market.models import Lot, Variety, PriceRecord

    # Get active varieties with live lots
    varieties = (
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

    # Get featured lots
    featured_lots = Lot.objects.filter(status=Lot.STATUS_ACTIVE, is_available=True, is_featured=True).select_related(
        "variety", "merchant", "mill"
    )[:6]

    # Get recent price updates
    recent_updates = PriceRecord.objects.select_related("variety").order_by("-recorded_at")[:10]

    # Stats
    total_varieties = Variety.objects.filter(is_active=True).count()
    total_lots = Lot.objects.filter(status=Lot.STATUS_ACTIVE, is_available=True).count()
    total_merchants = User.objects.filter(role=User.ROLE_MERCHANT, is_approved=True).count()

    context = {
        "varieties": varieties,
        "featured_lots": featured_lots,
        "recent_updates": recent_updates,
        "total_varieties": total_varieties,
        "total_lots": total_lots,
        "total_merchants": total_merchants,
    }
    return render(request, "core/home.html", context)
