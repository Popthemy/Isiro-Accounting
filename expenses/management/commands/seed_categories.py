"""Seed default categories for a newly registered user.

Called automatically on signup via the ``ensure_default_categories``
helper, but also available as a management command for testing.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from expenses.models import Category


DEFAULT_CATEGORIES = [
    {"name": "Food", "icon": "fa-utensils", "color": "#4F46E5"},
    {"name": "Transport", "icon": "fa-car", "color": "#10B981"},
    {"name": "Shopping", "icon": "fa-bag-shopping", "color": "#EF4444"},
    {"name": "Bills", "icon": "fa-file-invoice-dollar", "color": "#F59E0B"},
    {"name": "Entertainment", "icon": "fa-film", "color": "#0EA5E9"},
    {"name": "Health", "icon": "fa-heart-pulse", "color": "#EC4899"},
    {"name": "Travel", "icon": "fa-plane", "color": "#8B5CF6"},
    {"name": "Education", "icon": "fa-graduation-cap", "color": "#14B8A6"},
    {"name": "Salary", "icon": "fa-money-bill-trend-up", "color": "#22C55E"},
    {"name": "Investment", "icon": "fa-chart-line", "color": "#3B82F6"},
]


def ensure_default_categories(user):
    """Create the default category set for *user* if they have none."""
    if Category.objects.filter(user=user).exists():
        return
    for cat in DEFAULT_CATEGORIES:
        Category.objects.create(
            name=cat["name"], icon=cat["icon"], color=cat["color"],
            is_default=True, user=user,
        )


class Command(BaseCommand):
    help = "Seed default categories for all existing users."

    def handle(self, *args, **options):
        User = get_user_model()
        for user in User.objects.all():
            ensure_default_categories(user)
        self.stdout.write(self.style.SUCCESS("Default categories seeded."))
