"""Analytics service — aggregates transaction data for dashboards and reports.

Keeping this logic out of the views makes it reusable and easy to unit-test,
which matters for a final-year project defense.
"""

from collections import OrderedDict
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from expenses.models import Expense


def _month_range(months_ago: int = 0):
    """Return ``(start, end)`` datetimes for the current month offset by months_ago."""
    now = timezone.now()
    first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start = first - timedelta(days=30 * months_ago)
    if months_ago == 0:
        end = now
    else:
        end = first
    return start, end


def dashboard_stats(user):
    """Return the header-card figures for the dashboard."""
    start, end = _month_range(0)
    qs = Expense.objects.filter(user=user, date__gte=start.date(), date__lte=end.date())
    expenses = qs.filter(transaction_type=Expense.TransactionType.EXPENSE).aggregate(
        t=Sum("amount"))["t"] or 0
    income = qs.filter(transaction_type=Expense.TransactionType.INCOME).aggregate(
        t=Sum("amount"))["t"] or 0
    balance = income - expenses
    savings_pct = round((balance / income) * 100, 1) if income > 0 else 0
    savings_amount = balance if balance > 0 else 0

    all_expenses = Expense.objects.filter(
        user=user, transaction_type=Expense.TransactionType.EXPENSE).aggregate(
        t=Sum("amount"))["t"] or 0
    all_income = Expense.objects.filter(
        user=user, transaction_type=Expense.TransactionType.INCOME).aggregate(
        t=Sum("amount"))["t"] or 0
    total_balance = all_income - all_expenses

    remaining_budget = user.monthly_budget_preference - expenses if user.monthly_budget_preference else 0

    return {
        "month_expenses": expenses,
        "total_income": income,
        "balance": balance,
        "savings_pct": savings_pct,
        "savings_amount": savings_amount,
        "total_balance": total_balance,
        "remaining_budget": remaining_budget,
    }


def category_breakdown(user, months_ago: int = 0):
    """Return ``[(category_name, color, total), …]`` for the pie chart."""
    start, end = _month_range(months_ago)
    qs = (
        Expense.objects
        .filter(user=user, transaction_type=Expense.TransactionType.EXPENSE,
                date__gte=start.date(), date__lte=end.date())
        .values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    return [
        (row["category__name"] or "Uncategorised",
         row["category__color"] or "#6B7280",
         float(row["total"] or 0))
        for row in qs
    ]


def monthly_spending(user, months: int = 6):
    """Return ``OrderedDict`` of last N months: ``{'2024-01': 1234.5}``."""
    now = timezone.now()
    result = OrderedDict()
    for i in range(months - 1, -1, -1):
        d = (now.replace(day=1) - timedelta(days=30 * i))
        label = d.strftime("%b %Y")
        total = (
            Expense.objects
            .filter(user=user, transaction_type=Expense.TransactionType.EXPENSE,
                    date__year=d.year, date__month=d.month)
            .aggregate(t=Sum("amount"))["t"] or 0
        )
        result[label] = float(total)
    return result


def weekly_expenses(user, weeks: int = 8):
    """Return ``OrderedDict`` of last N weeks of expense totals."""
    now = timezone.now()
    result = OrderedDict()
    for i in range(weeks - 1, -1, -1):
        end = now - timedelta(weeks=i)
        start = end - timedelta(days=7)
        total = (
            Expense.objects
            .filter(user=user, transaction_type=Expense.TransactionType.EXPENSE,
                    date__gte=start.date(), date__lte=end.date())
            .aggregate(t=Sum("amount"))["t"] or 0
        )
        result[end.strftime("%d %b")] = float(total)
    return result


def recent_transactions(user, limit: int = 8):
    return list(Expense.objects.filter(user=user).select_related("category")[:limit])
