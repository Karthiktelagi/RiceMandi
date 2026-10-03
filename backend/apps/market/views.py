from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Avg, Count, Max, Min, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST

from apps.market.forms import LotForm, VarietyForm
from apps.market.models import Lot, Mill, PriceRecord, Variety, Watch
from apps.market.permissions import admin_required, approved_merchant_required


@require_GET
def home_redirect(request):
    return redirect("core:home")


@require_GET
def variety_list(request):
    varieties = Variety.objects.filter(is_active=True).order_by("name")
    return render(request, "market/variety_list.html", {"varieties": varieties})


@require_GET
@login_required
def variety_manage(request):
    user = request.user
    if user.role == user.ROLE_ADMIN or user.is_superuser:
        varieties = Variety.objects.all().select_related("created_by")
    elif user.role == user.ROLE_MERCHANT and user.is_approved:
        varieties = Variety.objects.filter(created_by=user).select_related("created_by") | Variety.objects.filter(
            created_by__isnull=True
        ).select_related("created_by")
        varieties = varieties.distinct().order_by("name")
    else:
        varieties = Variety.objects.filter(is_active=True).order_by("name")

    varieties = varieties.annotate(
        live_lots=Count("lots", filter=Q(lots__status=Lot.STATUS_ACTIVE, lots__is_available=True))
    )

    total = varieties.count() if hasattr(varieties, "count") else len(varieties)
    context = {
        "varieties": varieties,
        "total": total,
    }
    return render(request, "market/variety_manage.html", context)


@approved_merchant_required
def variety_create(request):
    if request.method == "POST":
        form = VarietyForm(request.POST, request.FILES)
        if form.is_valid():
            variety = form.save(commit=False)
            variety.created_by = request.user
            try:
                variety.save()
                messages.success(request, _("Variety created successfully."))
                return redirect("market:variety_manage")
            except Exception:
                messages.error(request, _("This variety already exists. Use the existing variety instead."))
    else:
        form = VarietyForm()
    return render(request, "market/variety_form.html", {"form": form, "is_create": True})


@login_required
def variety_edit(request, pk):
    variety = get_object_or_404(Variety, pk=pk)
    user = request.user

    can_edit = False
    if user.is_superuser or user.role == user.ROLE_ADMIN:
        can_edit = True
    elif user.role == user.ROLE_MERCHANT and user.is_approved and variety.created_by == user:
        can_edit = True

    if not can_edit:
        messages.error(request, _("You don't have permission to edit this variety."))
        return redirect("market:variety_manage")

    if request.method == "POST":
        form = VarietyForm(request.POST, request.FILES, instance=variety)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _("Variety updated successfully."))
                return redirect("market:variety_manage")
            except Exception:
                messages.error(request, _("This variety already exists. Use the existing variety instead."))
    else:
        form = VarietyForm(instance=variety)
    return render(request, "market/variety_form.html", {"form": form, "is_create": False, "variety": variety})


@login_required
@require_POST
def variety_toggle(request, pk):
    variety = get_object_or_404(Variety, pk=pk)
    user = request.user

    can_toggle = False
    if user.is_superuser or user.role == user.ROLE_ADMIN:
        can_toggle = True
    elif user.role == user.ROLE_MERCHANT and user.is_approved and variety.created_by == user:
        can_toggle = True

    if not can_toggle:
        messages.error(request, _("You don't have permission to change this variety."))
        return redirect("market:variety_manage")

    variety.is_active = not variety.is_active
    variety.save()
    action = _("activated") if variety.is_active else _("deactivated")
    messages.success(request, _("Variety %(name)s has been %(action)s.") % {"name": variety.name, "action": action})
    return redirect("market:variety_manage")


@require_GET
def variety_detail(request, pk):
    variety = get_object_or_404(Variety, pk=pk, is_active=True)
    lots = Lot.objects.filter(variety=variety, status=Lot.STATUS_ACTIVE, is_available=True).select_related(
        "merchant", "mill"
    )
    return render(request, "market/variety_detail.html", {"variety": variety, "lots": lots})


@require_GET
def mill_list(request):
    mills = Mill.objects.filter(is_active=True).order_by("name")
    return render(request, "market/mill_list.html", {"mills": mills})


@approved_merchant_required
def lot_create(request):
    if request.method == "POST":
        form = LotForm(request.POST, request.FILES)
        if form.is_valid():
            lot = form.save(commit=False)
            lot.merchant = request.user
            lot.save()
            messages.success(request, _("Lot posted successfully."))
            return redirect("market:my_lots")
    else:
        form = LotForm()
        form.fields["variety"].queryset = Variety.objects.filter(is_active=True).order_by("name")
        form.fields["mill"].queryset = Mill.objects.filter(is_active=True).order_by("name")
    return render(request, "market/lot_form.html", {"form": form, "is_create": True})


@approved_merchant_required
def lot_edit(request, pk):
    lot = get_object_or_404(Lot, pk=pk, merchant=request.user)
    if request.method == "POST":
        form = LotForm(request.POST, request.FILES, instance=lot)
        if form.is_valid():
            form.save()
            messages.success(request, _("Lot updated successfully."))
            return redirect("market:my_lots")
    else:
        form = LotForm(instance=lot)
        form.fields["variety"].queryset = Variety.objects.filter(is_active=True).order_by("name")
        form.fields["mill"].queryset = Mill.objects.filter(is_active=True).order_by("name")
    return render(request, "market/lot_form.html", {"form": form, "is_create": False, "lot": lot})


@approved_merchant_required
def my_lots(request):
    lots = Lot.objects.filter(merchant=request.user).select_related("variety", "mill").order_by("-created_at")
    return render(request, "market/my_lots.html", {"lots": lots})


@login_required
def lot_detail(request, pk):
    lot = get_object_or_404(Lot, pk=pk)
    return render(request, "market/lot_detail.html", {"lot": lot})


@login_required
def watch_toggle(request, pk):
    variety = get_object_or_404(Variety, pk=pk, is_active=True)
    watch, created = Watch.objects.get_or_create(user=request.user, variety=variety)
    if not created:
        watch.delete()
        messages.success(request, _("Removed from watchlist."))
    else:
        messages.success(request, _("Watching %(name)s") % {"name": variety.name})
    return redirect(request.META.get("HTTP_REFERER", reverse("market:variety_detail", args=[pk])))


@login_required
def watch_list(request):
    watches = Watch.objects.filter(user=request.user).select_related("variety")
    return render(request, "market/watch_list.html", {"watches": watches})


@login_required
def book_lot(request, pk):
    """First-come-first-serve booking queue."""
    from apps.market.models import Booking

    lot = get_object_or_404(Lot, pk=pk, status=Lot.STATUS_ACTIVE, is_available=True)
    if request.method == "POST":
        quantity = request.POST.get("quantity_quintal", "0")
        try:
            quantity = Decimal(quantity)
        except Exception:
            quantity = Decimal("0")
        if quantity <= 0:
            messages.error(request, _("Enter a valid quantity."))
            return redirect("market:lot_detail", pk=pk)
        if quantity > lot.quantity_quintal:
            messages.error(request, _("Not enough quantity available."))
            return redirect("market:lot_detail", pk=pk)

        # Get next queue position
        last_booking = Booking.objects.filter(lot=lot).order_by("-queue_position").first()
        next_position = (last_booking.queue_position + 1) if last_booking else 1

        booking, created = Booking.objects.get_or_create(
            lot=lot,
            buyer=request.user,
            defaults={
                "quantity_quintal": quantity,
                "queue_position": next_position,
                "status": Booking.STATUS_PENDING,
            },
        )
        if created:
            messages.success(
                request,
                _("You are #%(pos)d in queue for %(lot)s.") % {"pos": next_position, "lot": lot.variety.name},
            )
        else:
            messages.info(request, _("You already have a booking for this lot."))
        return redirect("market:lot_detail", pk=pk)
    return redirect("market:lot_detail", pk=pk)


@login_required
def my_bookings(request):
    from apps.market.models import Booking

    bookings = Booking.objects.filter(buyer=request.user).select_related("lot", "lot__variety", "lot__mill").order_by("-created_at")
    return render(request, "market/my_bookings.html", {"bookings": bookings})


@login_required
def negotiate_lot(request, pk):
    """Buyer proposes a price to merchant."""
    from apps.market.models import Negotiation

    lot = get_object_or_404(Lot, pk=pk, status=Lot.STATUS_ACTIVE, is_available=True)
    if request.method == "POST":
        buyer_price = request.POST.get("buyer_price", "0")
        quantity = request.POST.get("quantity_quintal", "0")
        message = request.POST.get("message", "")
        try:
            buyer_price = Decimal(buyer_price)
            quantity = Decimal(quantity)
        except Exception:
            buyer_price = Decimal("0")
            quantity = Decimal("0")
        if buyer_price <= 0:
            messages.error(request, _("Enter a valid price."))
            return redirect("market:lot_detail", pk=pk)

        negotiation, created = Negotiation.objects.get_or_create(
            lot=lot,
            buyer=request.user,
            defaults={
                "merchant": lot.merchant,
                "buyer_price": buyer_price,
                "quantity_quintal": quantity,
                "message": message,
                "status": Negotiation.STATUS_PENDING,
            },
        )
        if created:
            messages.success(request, _("Your offer has been sent to the merchant."))
        else:
            messages.info(request, _("You already have a pending negotiation for this lot."))
        return redirect("market:lot_detail", pk=pk)
    return redirect("market:lot_detail", pk=pk)


@login_required
def negotiation_list(request):
    """List negotiations for the current user (as buyer or merchant)."""
    from apps.market.models import Negotiation

    negotiations = Negotiation.objects.filter(
        models.Q(buyer=request.user) | models.Q(merchant=request.user)
    ).select_related("lot", "lot__variety", "buyer", "merchant").order_by("-created_at")
    return render(request, "market/negotiation_list.html", {"negotiations": negotiations})


@login_required
def negotiation_respond(request, pk):
    """Merchant responds to a negotiation (accept/reject/counter)."""
    from apps.market.models import Negotiation

    negotiation = get_object_or_404(Negotiation, pk=pk, merchant=request.user, status=Negotiation.STATUS_PENDING)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "accept":
            negotiation.status = Negotiation.STATUS_ACCEPTED
            negotiation.merchant_price = negotiation.buyer_price
            negotiation.save()
            messages.success(request, _("Offer accepted."))
        elif action == "reject":
            negotiation.status = Negotiation.STATUS_REJECTED
            negotiation.save()
            messages.info(request, _("Offer rejected."))
        elif action == "counter":
            counter_price = request.POST.get("counter_price", "0")
            try:
                counter_price = Decimal(counter_price)
            except Exception:
                counter_price = Decimal("0")
            if counter_price > 0:
                negotiation.merchant_price = counter_price
                negotiation.status = Negotiation.STATUS_COUNTERED
                negotiation.save()
                messages.success(request, _("Counter offer sent."))
            else:
                messages.error(request, _("Enter a valid counter price."))
        return redirect("market:negotiation_list")
    return redirect("market:negotiation_list")
