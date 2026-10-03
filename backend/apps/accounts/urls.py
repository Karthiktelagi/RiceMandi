from django.contrib.auth import views as auth_views
from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="registration/logout.html"), name="logout"),
    path("signup/", views.signup, name="signup"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("merchants/<int:pk>/approve/", views.merchant_approve, name="merchant_approve"),
    path("merchants/<int:pk>/reject/", views.merchant_reject, name="merchant_reject"),
]
