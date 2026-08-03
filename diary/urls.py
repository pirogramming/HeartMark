from django.urls import path
from . import views

app_name = "diary"
urlpatterns = [
    path("", views.diary_list, name="list"),
]