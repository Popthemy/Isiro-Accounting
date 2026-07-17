"""Authentication and profile views."""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from .forms import (
    CustomPasswordChangeForm,
    LoginForm,
    ProfileForm,
    SignUpForm,
    ProfileInfoForm,
    PreferenceForm,
    NotificationForm
)
from .models import User
from expenses.management.commands.seed_categories import ensure_default_categories


class SignUpView(View):
    """Register a new user account."""

    template_name = "users/signup.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return render(request, self.template_name, {"form": SignUpForm()})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            ensure_default_categories(user)
            login(request, user)
            messages.success(request, f"Welcome to Isiro, {user.full_name}!")
            return redirect("dashboard")
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    """Log an existing user in via email + password."""

    template_name = "users/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return render(request, self.template_name, {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(
                request, f"Welcome back, {user.full_name or user.email}!")
            return redirect("dashboard")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    """Log the current user out."""

    def post(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect("landing")


class ProfileView(LoginRequiredMixin, View):
    """View and edit profile, notification and currency settings."""

    template_name = "users/profile.html"
    login_url = "users:login"

    def dispatch(self, request, *args, **kwargs):
        print("PROFILE VIEW DISPATCH HIT")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = ProfileForm(instance=request.user)

        print("User:", request.user)
        print("Initial:", form.initial)

        return render(request, self.template_name, {
            "profile_form": ProfileInfoForm(instance=request.user),
            "preference_form": PreferenceForm(instance=request.user),
            "notification_form": NotificationForm(instance=request.user),
            "password_form": CustomPasswordChangeForm(request.user),
        })

    def post(self, request):
        print(f"posted data {request.POST}")

        if "update_profile" in request.POST:
            profile_form = ProfileInfoForm(
                request.POST,
                request.FILES,
                instance=request.user
            )

            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("users:profile")

        elif "update_preferences" in request.POST:
            preference_form = PreferenceForm(
                request.POST,
                instance=request.user
            )

            if preference_form.is_valid():
                preference_form.save()
                messages.success(request, "Preferences updated successfully.")
                return redirect("users:profile")

        elif "update_notifications" in request.POST:
            notification_form = NotificationForm(
                request.POST,
                instance=request.user
            )

            if notification_form.is_valid():
                notification_form.save()
                messages.success(request, "Notifications updated successfully.")
                return redirect("users:profile")

        elif "change_password" in request.POST:
            password_form = CustomPasswordChangeForm(
                request.user,
                request.POST
            )

            if password_form.is_valid():
                password_form.save()
                messages.success(request, "Password changed successfully.")
                return redirect("users:profile")

        return redirect("users:profile")

class DeleteAccountView(LoginRequiredMixin, View):
    """Permanently delete the logged-in user's account."""

    login_url = "users:login"

    def post(self, request):
        user = request.user
        logout(request)
        user.delete()
        messages.info(request, "Your account has been deleted.")
        return redirect("landing")
