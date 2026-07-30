from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("common.urls")),
    path("accounts/", include("accounts.urls")),
    path("locations/", include("locations.urls")),
    path("records/", include("records.urls")),
    path("diary/", include("diary.urls")),
]

