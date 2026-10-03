from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.market.models import Booking, Lot, TraderRating
from apps.notifications.models import Notification


@login_required
def notification_list(request):
    """List all notifications for the current user."""
    notifications = Notification.objects.filter(recipient=request.user).order_by("-created_at")
    unread_count = notifications.filter(is_read=False).count()
    return render(
        request,
        "notifications/notification_list.html",
        {"notifications": notifications, "unread_count": unread_count},
    )


@login_required
def notification_mark_read(request, pk):
    """Mark a single notification as read."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    if notification.url:
        return redirect(notification.url)
    return redirect("notifications:list")


@login_required
def notification_mark_all_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect("notifications:list")


@login_required
def rate_booking(request, booking_id):
    """Rate a completed booking (buyer rates merchant)."""
    booking = get_object_or_404(Booking, pk=booking_id, buyer=request.user, status=Booking.STATUS_COMPLETED)

    # Check if already rated
    if TraderRating.objects.filter(rater=request.user, rated=booking.lot.merchant, lot=booking.lot).exists():
        from django.contrib import messages

        messages.info(request, _("You have already rated this booking."))
        return redirect("market:my_bookings")

    if request.method == "POST":
        from django.contrib import messages

        rating_value = request.POST.get("rating", 0)
        comment = request.POST.get("comment", "")
        try:
            rating_value = int(rating_value)
        except (ValueError, TypeError):
            rating_value = 0

        if rating_value < 1 or rating_value > 5:
            messages.error(request, _("Please select a rating between 1 and 5."))
            return redirect("market:my_bookings")

        TraderRating.objects.create(
            rater=request.user,
            rated=booking.lot.merchant,
            lot=booking.lot,
            rating=rating_value,
            comment=comment,
        )
        messages.success(request, _("Thank you for your rating!"))
        return redirect("market:my_bookings")

    return render(request, "market/rate_booking.html", {"booking": booking})


@login_required
def merchant_ratings(request, merchant_id):
    """Show all ratings for a merchant."""
    from apps.accounts.models import User

    merchant = get_object_or_404(User, pk=merchant_id, role=User.ROLE_MERCHANT)
    ratings = TraderRating.objects.filter(rated=merchant).select_related("rater", "lot", "lot__variety").order_by(
        "-created_at"
    )
    avg_rating = ratings.aggregate(avg=Avg("rating"))["avg"] or 0
    rating_count = ratings.count()

    return render(
        request,
        "market/merchant_ratings.html",
        {
            "merchant": merchant,
            "ratings": ratings,
            "avg_rating": round(avg_rating, 1),
            "rating_count": rating_count,
        },
    )


@login_required
def merchant_bookings(request):
    """Merchant view to manage bookings for their lots."""
    bookings = (
        Booking.objects.filter(lot__merchant=request.user)
        .select_related("buyer", "lot", "lot__variety", "lot__mill")
        .order_by("lot", "queue_position")
    )
    return render(request, "market/merchant_bookings.html", {"bookings": bookings})


@login_required
@require_POST
def booking_update_status(request, pk):
    """Merchant updates booking status (confirm/cancel/complete)."""
    from django.contrib import messages

    booking = get_object_or_404(Booking, pk=pk, lot__merchant=request.user)
    new_status = request.POST.get("status")

    valid_statuses = [Booking.STATUS_CONFIRMED, Booking.STATUS_CANCELLED, Booking.STATUS_COMPLETED]
    if new_status in valid_statuses:
        booking.status = new_status
        booking.save(update_fields=["status"])
        messages.success(request, _("Booking #%(pos)d status updated to %(status)s.") % {"pos": booking.queue_position, "status": new_status})
    else:
        messages.error(request, _("Invalid status."))

    return redirect("market:merchant_bookings")
