from django.urls import path

from apps.market import api

app_name = "market_api"

urlpatterns = [
    path("", api.api_root, name="root"),
    path("varieties/", api.VarietyListAPIView.as_view(), name="variety_list"),
    path("lots/", api.LotListAPIView.as_view(), name="lot_list"),
]
