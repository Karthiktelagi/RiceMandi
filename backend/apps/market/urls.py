from django.urls import path

from apps.market import views

app_name = "market"

urlpatterns = [
    path("", views.home_redirect, name="index"),
    path("varieties/", views.variety_list, name="variety_list"),
    path("varieties/manage/", views.variety_manage, name="variety_manage"),
    path("varieties/manage/new/", views.variety_create, name="variety_create"),
    path("varieties/manage/<int:pk>/edit/", views.variety_edit, name="variety_edit"),
    path("varieties/manage/<int:pk>/toggle/", views.variety_toggle, name="variety_toggle"),
    path("varieties/<int:pk>/", views.variety_detail, name="variety_detail"),
    path("mills/", views.mill_list, name="mill_list"),
    path("merchant/lots/new/", views.lot_create, name="lot_create"),
    path("merchant/lots/", views.my_lots, name="my_lots"),
    path("lots/<int:pk>/", views.lot_detail, name="lot_detail"),
    path("merchant/lots/<int:pk>/edit/", views.lot_edit, name="lot_edit"),
    path("varieties/<int:pk>/watch/", views.watch_toggle, name="watch_toggle"),
    path("watch/", views.watch_list, name="watch_list"),
    path("lots/<int:pk>/book/", views.book_lot, name="book_lot"),
    path("lots/<int:pk>/negotiate/", views.negotiate_lot, name="negotiate_lot"),
    path("lots/<int:pk>/enquire/", views.enquire_lot, name="enquire_lot"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("my-bookings/<int:booking_id>/rate/", views.rate_booking, name="rate_booking"),
    path("negotiations/", views.negotiation_list, name="negotiation_list"),
    path("negotiations/<int:pk>/respond/", views.negotiation_respond, name="negotiation_respond"),
    path("merchant/bookings/", views.merchant_bookings, name="merchant_bookings"),
    path("merchant/bookings/<int:pk>/update/", views.booking_update_status, name="booking_update_status"),
    path("merchant/<int:merchant_id>/ratings/", views.merchant_ratings, name="merchant_ratings"),
]
