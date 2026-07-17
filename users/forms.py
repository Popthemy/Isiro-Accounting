"""Forms for authentication and profile management."""

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordChangeForm,
)

from .models import User


class SignUpForm(UserCreationForm):
    """Registration form capturing full name, email and password."""

    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Jane Doe"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-input", "placeholder": "jane@example.com"}),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-input", "placeholder": "At least 8 characters"}),
        label="Password",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-input", "placeholder": "Repeat password"}),
        label="Confirm password",
    )

    class Meta:
        model = User
        fields = ("full_name", "email", "password1", "password2")


class LoginForm(AuthenticationForm):
    """Login form using email + password."""

    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-input", "placeholder": "jane@example.com"}),
        label="Email",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-input", "placeholder": "Your password"}),
    )


class ProfileInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "full_name",
            "email",
            "profile_image",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "profile_image": forms.FileInput(attrs={"class": "form-input"}),

        }


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "currency",
            "monthly_budget_preference",
            "theme_preference",
        ]
        widgets = {
            "currency": forms.Select(
                choices=[("USD", "USD $"), ("EUR", "EUR €"), ("GBP", "GBP £"),
                         ("KES", "KES KSh"), ("NGN", "NGN ₦"), ("INR", "INR ₹"),
                         ("RWF", "RWF FRw")],
                attrs={"class": "form-input"},
            ),
            "monthly_budget_preference": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0"}),
            "theme_preference": forms.Select(choices=[("light", "Light"), ("dark", "Dark")], attrs={"class": "form-input"}),
        }


class NotificationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "notify_expenses",
            "notify_budgets",
            "notify_imports",
        ]
        widgets = {

            "notify_expenses": forms.CheckboxInput(attrs={"class": "form-check"}),
            "notify_budgets": forms.CheckboxInput(attrs={"class": "form-check"}),
            "notify_imports": forms.CheckboxInput(attrs={"class": "form-check"}),
        }


class ProfileForm(forms.ModelForm):
    """Editable profile fields shown on the settings page."""

    class Meta:
        model = User
        fields = ("full_name", "email", "profile_image", "currency",
                  "monthly_budget_preference", "theme_preference",
                  "notify_expenses", "notify_budgets", "notify_imports")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "profile_image": forms.FileInput(attrs={"class": "form-input"}),
            "currency": forms.Select(
                choices=[("USD", "USD $"), ("EUR", "EUR €"), ("GBP", "GBP £"),
                         ("KES", "KES KSh"), ("NGN", "NGN ₦"), ("INR", "INR ₹"),
                         ("RWF", "RWF FRw")],
                attrs={"class": "form-input"},
            ),
            "monthly_budget_preference": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0"}),
            "theme_preference": forms.Select(choices=[("light", "Light"), ("dark", "Dark")], attrs={"class": "form-input"}),
            "notify_expenses": forms.CheckboxInput(attrs={"class": "form-check"}),
            "notify_budgets": forms.CheckboxInput(attrs={"class": "form-check"}),
            "notify_imports": forms.CheckboxInput(attrs={"class": "form-check"}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Password change form with Isiro input styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})
