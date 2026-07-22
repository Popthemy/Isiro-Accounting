from datetime import date

from django.test import TestCase

from expenses.models import Category, Expense, Wallet
from expenses.services.analytics import category_breakdown, dashboard_stats
from users.models import User


class DashboardAnalyticsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="tester@example.com",
            password="secret123",
            full_name="Test User",
            monthly_budget_preference=1000,
        )
        self.wallet = Wallet.objects.create(
            user=self.user,
            name="Main Wallet",
            opening_balance=500,
            current_balance=500,
        )
        self.category = Category.objects.create(
            user=self.user, name="Food", color="#FF0000")

    def test_dashboard_stats_and_category_breakdown_use_requested_date_range(self):
        Expense.objects.create(
            user=self.user,
            wallet=self.wallet,
            amount=50,
            date=date(2024, 5, 10),
            category=self.category,
            description="Lunch",
            transaction_type=Expense.TransactionType.EXPENSE,
        )
        Expense.objects.create(
            user=self.user,
            wallet=self.wallet,
            amount=120,
            date=date(2024, 6, 12),
            category=self.category,
            description="Dinner",
            transaction_type=Expense.TransactionType.EXPENSE,
        )
        Expense.objects.create(
            user=self.user,
            wallet=self.wallet,
            amount=200,
            date=date(2024, 5, 15),
            category=self.category,
            description="Salary",
            transaction_type=Expense.TransactionType.INCOME,
        )

        stats = dashboard_stats(self.user, start_date=date(
            2024, 5, 1), end_date=date(2024, 5, 31))
        breakdown = category_breakdown(self.user, start_date=date(
            2024, 5, 1), end_date=date(2024, 5, 31))

        self.assertEqual(stats["month_expenses"], 50)
        self.assertEqual(stats["total_income"], 200)
        self.assertEqual(stats["balance"], 150)
        self.assertEqual(breakdown, [("Food", "#FF0000", 50.0)])
