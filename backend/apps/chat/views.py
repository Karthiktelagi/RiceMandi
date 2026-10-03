from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.chat.models import Conversation, Message
from apps.market.models import Lot


@login_required
def conversation_list(request):
    """List all conversations for the current user."""
    conversations = Conversation.objects.filter(
        Q(buyer=request.user) | Q(merchant=request.user)
    ).select_related("buyer", "merchant", "lot", "lot__variety").order_by("-last_message_at")

    # Annotate with last message and unread count
    for conv in conversations:
        conv.last_message = conv.messages.order_by("-created_at").first()
        conv.unread_count = conv.messages.filter(read_at__isnull=True).exclude(sender=request.user).count()

    return render(request, "chat/conversation_list.html", {"conversations": conversations})


@login_required
def conversation_detail(request, pk):
    """View a conversation and send messages."""
    conversation = get_object_or_404(
        Conversation,
        Q(buyer=request.user) | Q(merchant=request.user),
        pk=pk,
    )
    messages_list = conversation.messages.select_related("sender").order_by("created_at")

    # Mark messages from the other user as read
    conversation.messages.filter(read_at__isnull=True).exclude(sender=request.user).update(read_at=timezone.now())

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            Message.objects.create(conversation=conversation, sender=request.user, body=body)
            conversation.last_message_at = timezone.now()
            conversation.save(update_fields=["last_message_at"])
            return redirect("chat:detail", pk=pk)

    return render(
        request,
        "chat/conversation_detail.html",
        {"conversation": conversation, "messages_list": messages_list},
    )


@login_required
@require_POST
def start_conversation(request, lot_id):
    """Start a conversation with a merchant about a lot (from enquiry)."""
    lot = get_object_or_404(Lot, pk=lot_id, status=Lot.STATUS_ACTIVE, is_available=True)

    if request.user == lot.merchant:
        messages.error(request, _("You cannot start a conversation with yourself."))
        return redirect("market:lot_detail", pk=lot_id)

    conversation, created = Conversation.objects.get_or_create(
        buyer=request.user,
        merchant=lot.merchant,
        lot=lot,
    )

    # If created, add an initial message
    if created:
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            body=_("Hello, I'm interested in your lot: %(lot)s") % {"lot": lot.variety.name},
        )

    return redirect("chat:detail", pk=conversation.pk)



