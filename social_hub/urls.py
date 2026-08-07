from django.urls import path

from . import views


app_name = "social_hub"

urlpatterns = [
    path("friends/", views.friend_management, name="friend_management"),
]
