from django.urls import path

from . import views

app_name = "record_sharing"

urlpatterns = [
    path("shared/", views.shared_list, name="shared_list"),
    path("shared/<int:pk>/", views.shared_detail, name="shared_detail"),
    path("shared/<int:pk>/comments/", views.comment_create, name="comment_create"),
    path(
        "shared/<int:pk>/comments/<int:comment_id>/delete/",
        views.comment_delete,
        name="comment_delete",
    ),
    path("records/<int:record_id>/share/", views.share_create, name="create"),
    path("records/<int:record_id>/revoke/", views.share_revoke, name="revoke"),
]
