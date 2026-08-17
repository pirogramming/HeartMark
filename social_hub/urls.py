from django.urls import path

from . import views


app_name = "social_hub"

urlpatterns = [
    path("friends/", views.friend_management, name="friend_management"),
    path("shared-records/", views.shared_records, name="shared_records"),
    path("sent-records/", views.sent_records, name="sent_records"),
]
