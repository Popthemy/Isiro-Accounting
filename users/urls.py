"""URL routes for the users app (namespace ``users``)."""

from django.urls import path

from .views import (
    DeleteAccountView,
    LoginView,
    LogoutView,
    ProfileView,
    SignUpView,
)

app_name = "users"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("delete/", DeleteAccountView.as_view(), name="delete_account"),
]
