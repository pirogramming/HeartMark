from django.urls import path

from . import views

app_name = "common"

urlpatterns = [
    path("", views.home, name="home"),
    path("tutorial/complete/", views.complete_home_tutorial, name="complete_home_tutorial"),
]
