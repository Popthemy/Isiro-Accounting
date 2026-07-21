from django.contrib import admin
from .models import Category, Expense, Wallet


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "color",
                    "is_default", "user", "created_at")
    list_filter = ("is_default",)
    search_fields = ("name",)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "account_type", "opening_balance",
                    "current_balance", "currency", "is_active", "created_at")
    list_filter = ("account_type", "is_active", "currency")
    search_fields = ("name", "user__email")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("user", "wallet", "amount", "date", "category",
                    "transaction_type", "payment_method", "source", "status")
    list_filter = ("transaction_type", "source",
                   "payment_method", "status", "date", "wallet")
    search_fields = ("description", "user__email",
                     "merchant_name", "wallet__name")
    date_hierarchy = "date"
