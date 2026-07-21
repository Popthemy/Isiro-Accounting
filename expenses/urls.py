from django.urls import path
from .views import (
    CategoryCreateView, CategoryDeleteView, CategoryListView, CategoryUpdateView,
    ExpenseCreateView, ExpenseDeleteView, ExpenseDetailView, ExpenseListView,
    ExpenseUpdateView, ReportsView, WalletCreateView, WalletDeleteView,
    WalletDetailView, WalletListView, WalletUpdateView,
)

app_name = "expenses"

urlpatterns = [
    path("", ExpenseListView.as_view(), name="list"),
    path("wallets/", WalletListView.as_view(), name="wallet_list"),
    path("wallets/add/", WalletCreateView.as_view(), name="wallet_add"),
    path("wallets/<int:pk>/", WalletDetailView.as_view(), name="wallet_detail"),
    path("wallets/<int:pk>/edit/", WalletUpdateView.as_view(), name="wallet_edit"),
    path("wallets/<int:pk>/delete/",
         WalletDeleteView.as_view(), name="wallet_delete"),
    path("add/", ExpenseCreateView.as_view(), name="add"),
    path("<int:pk>/", ExpenseDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", ExpenseUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", ExpenseDeleteView.as_view(), name="delete"),
    path("categories/", CategoryListView.as_view(), name="categories"),
    path("categories/add/", CategoryCreateView.as_view(), name="category_add"),
    path("categories/<int:pk>/edit/",
         CategoryUpdateView.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/",
         CategoryDeleteView.as_view(), name="category_delete"),
    path("reports/", ReportsView.as_view(), name="reports"),
]
