from django.urls import path

from apps.chat import views

app_name = "chat"

urlpatterns = [
    path("", views.conversation_list, name="list"),
    path("<int:pk>/", views.conversation_detail, name="detail"),
    path("start/<int:lot_id>/", views.start_conversation, name="start"),
]
