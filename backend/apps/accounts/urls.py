from django.contrib.auth import views as auth_views
from django.urls import path
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from apps.accounts import views

app_name = "accounts"


class LoginThrottleMixin:
    throttle_classes = [AnonRateThrottle]
    throttle_scope = "login"


urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="registration/logout.html"), name="logout"),
    path("signup/", views.signup, name="signup"),
    path("profile/", views.ProfileUpdateView.as_view(), name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("merchants/<int:pk>/approve/", views.merchant_approve, name="merchant_approve"),
    path("merchants/<int:pk>/reject/", views.merchant_reject, name="merchant_reject"),
]
