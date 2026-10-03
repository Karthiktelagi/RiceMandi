from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("admin/", admin.site.urls),
    # Translation catalogue for HTMX/Bootstrap widgets that need client-side strings.
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("", include("apps.core.urls")),
    path("", include("apps.accounts.urls")),
    path("", include("apps.market.urls")),
    path("", include("apps.chat.urls")),
    path("", include("apps.notifications.urls")),
    path("api/v1/", include("apps.market.api_urls")),
]

if settings.DEBUG:
    # Serve uploaded lot and variety photos straight from MEDIA_ROOT in dev.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
