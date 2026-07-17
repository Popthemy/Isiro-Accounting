from django.contrib import admin
from .models import Budget

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "category", "amount_limit", "period_type", "is_active", "start_date", "end_date")
    list_filter = ("period_type", "is_active")
    search_fields = ("name", "user__email")
