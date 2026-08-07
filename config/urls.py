from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("common.urls")),
    path("accounts/", include("accounts.urls")),
    path("mypage/", include("mypage.urls")),
    path("accounts/", include("allauth.urls")),
    path("locations/", include("locations.urls")),
    path("records/", include("records.urls")),
    path("diary/", include("diary.urls")),
    path("", include("social_hub.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
