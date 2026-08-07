from django.urls import path

from . import views

app_name = "friendships"

urlpatterns = [
    path("", views.friend_list, name="list"),
    path("invite/", views.invite_link, name="invite_link"),
    path("invite/<str:code>/", views.invite_detail, name="invite_detail"),
    path("requests/send/<int:user_id>/", views.send_request, name="send_request"),
    path("requests/<int:pk>/<str:action>/", views.respond_request, name="respond_request"),
    path("friends/<int:user_id>/delete/", views.friend_delete, name="friend_delete"),
]
