"""Budget model for tracking spending limits per category."""

from django.conf import settings
from django.db import models

from expenses.models import Category


class Budget(models.Model):
    """A spending limit for a category over a time period."""

    class PeriodType(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets",
    )
    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="budgets",
    )
    amount_limit = models.DecimalField(max_digits=12, decimal_places=2)
    period_type = models.CharField(
        max_length=10, choices=PeriodType.choices, default=PeriodType.MONTHLY,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    alert_percentage = models.IntegerField(default=80)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} — {self.category.name}"

    @property
    def spent_amount(self):
        from expenses.models import Expense
        qs = Expense.objects.filter(
            user=self.user, category=self.category,
            transaction_type=Expense.TransactionType.EXPENSE,
            date__gte=self.start_date, date__lte=self.end_date,
        )
        return qs.aggregate(t=models.Sum("amount"))["t"] or 0

    @property
    def remaining(self):
        return self.amount_limit - self.spent_amount

    @property
    def spent_percentage(self):
        if self.amount_limit > 0:
            return min(100, int((self.spent_amount / self.amount_limit) * 100))
        return 0

    @property
    def is_warning(self):
        return self.spent_percentage >= self.alert_percentage

    @property
    def is_exceeded(self):
        return self.spent_amount >= self.amount_limit
