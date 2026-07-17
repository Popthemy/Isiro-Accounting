"""User model for the Isiro platform.

Extends Django's ``AbstractUser`` to add full-name and profile-image
fields while keeping the built-in authentication machinery intact.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Manager that uses email instead of username as the identifier."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user identified by email with optional profile image."""

    username = None  # remove the username field; use email instead

    full_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True,
    )
    currency = models.CharField(max_length=10, default="USD")
    monthly_budget_preference = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    theme_preference = models.CharField(max_length=10, default="light", choices=[("light", "Light"), ("dark", "Dark")])
    notify_expenses = models.BooleanField(default=True)
    notify_budgets = models.BooleanField(default=True)
    notify_imports = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    def __str__(self) -> str:
        return self.full_name or self.email

    @property
    def initials(self) -> str:
        """Return up to two uppercase initials for the avatar badge."""
        name = self.full_name or self.email
        parts = [p for p in name.replace("@", " ").split() if p]
        return "".join(p[0].upper() for p in parts[:2]) or "?"
