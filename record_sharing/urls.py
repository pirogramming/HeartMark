from django.urls import path

from . import views

app_name = "record_sharing"

urlpatterns = [
    path("shared/", views.shared_list, name="shared_list"),
    path("shared/<int:pk>/", views.shared_detail, name="shared_detail"),
    path("records/<int:record_id>/share/", views.share_create, name="create"),
    path("records/<int:record_id>/revoke/", views.share_revoke, name="revoke"),
]
