"""Analytics service — aggregates transaction data for dashboards and reports.

Keeping this logic out of the views makes it reusable and easy to unit-test,
which matters for a final-year project defense.
"""

from collections import OrderedDict
from datetime import date, timedelta

from django.db.models import Sum
from django.utils import timezone

from expenses.models import Expense, Wallet


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


def _coerce_date(value):
    if isinstance(value, date):
        return value
    if not value:
        return None
    return timezone.datetime.strptime(str(value), "%Y-%m-%d").date()


def dashboard_stats(user, start_date=None, end_date=None):
    """Return the header-card figures for the dashboard."""
    if start_date is None or end_date is None:
        start, end = _month_range(0)
        start_date = start.date()
        end_date = end.date()
    qs = Expense.objects.filter(
        user=user, date__gte=start_date, date__lte=end_date)
    expenses = qs.filter(transaction_type=Expense.TransactionType.EXPENSE).aggregate(
        t=Sum("amount"))["t"] or 0
    income = qs.filter(transaction_type=Expense.TransactionType.INCOME).aggregate(
        t=Sum("amount"))["t"] or 0
    balance = income - expenses
    savings_pct = round((balance / income) * 100, 1) if income > 0 else 0
    savings_amount = balance if balance > 0 else 0

    total_balance = Wallet.objects.filter(user=user, is_active=True).aggregate(
        t=Sum("current_balance"))["t"] or 0

    remaining_budget = user.monthly_budget_preference - \
        expenses if user.monthly_budget_preference else 0

    return {
        "month_expenses": expenses,
        "total_income": income,
        "balance": balance,
        "savings_pct": savings_pct,
        "savings_amount": savings_amount,
        "total_balance": total_balance,
        "remaining_budget": remaining_budget,
    }


def category_breakdown(user, months_ago: int = 0, start_date=None, end_date=None):
    """Return ``[(category_name, color, total), …]`` for the pie chart."""
    if start_date is None or end_date is None:
        start, end = _month_range(months_ago)
        start_date = start.date()
        end_date = end.date()
    qs = (
        Expense.objects
        .filter(user=user, transaction_type=Expense.TransactionType.EXPENSE,
                date__gte=start_date, date__lte=end_date)
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


def monthly_spending(user, months: int = 6, start_date=None, end_date=None):
    """Return an ``OrderedDict`` of monthly totals for the requested range."""
    if start_date and end_date:
        result = OrderedDict()
        current = start_date.replace(day=1)
        last = end_date.replace(day=1)
        while current <= last:
            label = current.strftime("%b %Y")
            total = (
                Expense.objects
                .filter(user=user, transaction_type=Expense.TransactionType.EXPENSE,
                        date__year=current.year, date__month=current.month)
                .aggregate(t=Sum("amount"))["t"] or 0
            )
            result[label] = float(total)
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        return result

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


def weekly_expenses(user, weeks: int = 8, start_date=None, end_date=None):
    """Return an ``OrderedDict`` of weekly expense totals for the requested range."""
    if start_date and end_date:
        result = OrderedDict()
        current_start = start_date
        while current_start <= end_date:
            current_end = min(current_start + timedelta(days=6), end_date)
            label = f"{current_start.strftime('%d %b')} - {current_end.strftime('%d %b')}"
            total = (
                Expense.objects
                .filter(user=user, transaction_type=Expense.TransactionType.EXPENSE,
                        date__gte=current_start, date__lte=current_end)
                .aggregate(t=Sum("amount"))["t"] or 0
            )
            result[label] = float(total)
            current_start = current_end + timedelta(days=1)
        return result

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


def recent_transactions(user, limit: int = 8, start_date=None, end_date=None):
    qs = Expense.objects.filter(user=user).select_related("category")
    if start_date and end_date:
        qs = qs.filter(date__gte=start_date, date__lte=end_date)
    return list(qs[:limit])
