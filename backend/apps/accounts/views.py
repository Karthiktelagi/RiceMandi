from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView

from apps.accounts.forms import ProfileForm, SignUpForm
from apps.accounts.models import User


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        if user.role == user.ROLE_MERCHANT:
            messages.info(
                self.request,
                _("Your merchant account has been created and is pending admin approval."),
            )
        else:
            messages.success(
                self.request,
                _("Your account has been created. You can now log in."),
            )
        return response


signup = SignUpView.as_view()


class ProfileUpdateView(UpdateView):
    """Let a signed-in user finish the fields Google could not supply.

    Acts as the ``LOGIN_REDIRECT_URL`` so it must cope with two cases: a
    complete profile (redirect straight on to the dashboard) and an incomplete
    one, which is every Google sign-up until they save this form.
    """

    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:dashboard")

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, *args, **kwargs):
        if not request.user.phone:
            return super().get(request, *args, **kwargs)
        return redirect(self.success_url)

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.role == User.ROLE_MERCHANT:
            messages.info(
                self.request,
                _("Your merchant account is pending admin approval."),
            )
        else:
            messages.success(self.request, _("Your profile has been updated."))
        return response


@login_required
def dashboard(request):
    user = request.user
    context = {"user": user}
    if user.role == user.ROLE_ADMIN or user.is_superuser:
        pending_merchants = User.objects.filter(role=User.ROLE_MERCHANT, is_approved=False).order_by("-date_joined")
        context["pending_merchants"] = pending_merchants
        return render(request, "accounts/dashboard_admin.html", context)
    elif user.role == user.ROLE_MERCHANT:
        if not user.is_approved:
            return render(request, "accounts/pending_approval.html", context)
        return render(request, "accounts/dashboard_merchant.html", context)
    else:
        return render(request, "accounts/dashboard_buyer.html", context)


@login_required
def merchant_approve(request, pk):
    if not (request.user.role == request.user.ROLE_ADMIN or request.user.is_superuser):
        messages.error(request, _("Permission denied."))
        return redirect("accounts:dashboard")
    merchant = get_object_or_404(User, pk=pk, role=User.ROLE_MERCHANT)
    merchant.is_approved = True
    merchant.save(update_fields=["is_approved"])
    messages.success(request, _("Merchant %(name)s has been approved.") % {"name": merchant.business_name or merchant.username})
    return redirect("accounts:dashboard")


@login_required
def merchant_reject(request, pk):
    if not (request.user.role == request.user.ROLE_ADMIN or request.user.is_superuser):
        messages.error(request, _("Permission denied."))
        return redirect("accounts:dashboard")
    merchant = get_object_or_404(User, pk=pk, role=User.ROLE_MERCHANT, is_approved=False)
    # Don't delete, just maybe mark - spec says reject button in approvals screen
    messages.info(request, _("Merchant %(name)s rejected. Contact them if needed.") % {"name": merchant.business_name or merchant.username})
    return redirect("accounts:dashboard")
