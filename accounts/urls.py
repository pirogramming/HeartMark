from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("character/", views.character_select_view, name="character_select"),
    path("logout/", views.logout_view, name="logout"),
]
