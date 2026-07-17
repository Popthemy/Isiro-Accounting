"""Root URL configuration for the Isiro platform."""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from expenses.views import DashboardView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Landing page
    path("", TemplateView.as_view(template_name="landing.html"), name="landing"),

    # Auth / users
    path("users/", include(("users.urls", "users"), namespace="users")),

    # Main dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    # Expenses
    path("expenses/", include(("expenses.urls", "expenses"), namespace="expenses")),

    # Income (uses expenses app views with income type)
    path("income/", include(("expenses.urls_income", "income"), namespace="income")),

    # Budgets
    path("budgets/", include(("budgets.urls", "budgets"), namespace="budgets")),

    # Imports
    path("imports/", include(("imports.urls", "imports"), namespace="imports")),

    # Notifications
    path("notifications/", include(("notifications.urls", "notifications"), namespace="notifications")),

    # Core (activity logs etc.)
    path("core/", include(("core.urls", "core"), namespace="core")),
]
