from django.contrib import admin
from .models import Category, Expense

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "color", "is_default", "user", "created_at")
    list_filter = ("is_default",)
    search_fields = ("name",)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "date", "category", "transaction_type", "payment_method", "source", "status")
    list_filter = ("transaction_type", "source", "payment_method", "status", "date")
    search_fields = ("description", "user__email", "merchant_name")
    date_hierarchy = "date"
