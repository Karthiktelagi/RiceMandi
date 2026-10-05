from django.urls import path

from apps.core import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    # Named `set_language` to match Django's own convention.
    path("lang/<str:code>/", views.set_language, name="set_language"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
]
