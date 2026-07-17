"""Views for the expenses app — dashboard, CRUD, categories, reports."""

import csv
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from budgets.models import Budget
from notifications.models import Notification

from .forms import CategoryForm, ExpenseForm
from .models import Category, Expense
from .services.analytics import (
    category_breakdown,
    dashboard_stats,
    monthly_spending,
    recent_transactions,
    weekly_expenses,
)


class DashboardView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "dashboard.html"

    def get(self, request):
        stats = dashboard_stats(request.user)
        pie = category_breakdown(request.user)
        line = monthly_spending(request.user)
        bar = weekly_expenses(request.user)
        recent = recent_transactions(request.user)
        budgets = Budget.objects.filter(user=request.user, is_active=True).select_related("category")[:5]
        notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return render(request, self.template_name, {
            "stats": stats, "pie_data": pie, "line_data": line, "bar_data": bar,
            "recent": recent, "budgets": budgets, "notifications": notifications,
            "unread_count": unread_count, "currency": request.user.currency,
            "today": timezone.now(),
        })


class ExpenseListView(LoginRequiredMixin, ListView):
    login_url = "users:login"
    template_name = "expenses/expense_list.html"
    context_object_name = "expenses"
    paginate_by = 15

    def get_queryset(self):
        qs = Expense.objects.filter(user=self.request.user).select_related("category")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(description__icontains=q) | Q(category__name__icontains=q) | Q(merchant_name__icontains=q))
        ttype = self.request.GET.get("type")
        if ttype in ("expense", "income"):
            qs = qs.filter(transaction_type=ttype)
        cat = self.request.GET.get("category")
        if cat:
            qs = qs.filter(category_id=cat)
        date_from = self.request.GET.get("date_from")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        date_to = self.request.GET.get("date_to")
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.filter(user=self.request.user)
        ctx["currency"] = self.request.user.currency
        return ctx


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    login_url = "users:login"
    template_name = "expenses/expense_detail.html"
    context_object_name = "expense"

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    login_url = "users:login"
    template_name = "expenses/add_expense.html"
    form_class = ExpenseForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Transaction added successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.GET.get("next") or "/expenses/"


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "users:login"
    template_name = "expenses/edit_expense.html"
    form_class = ExpenseForm
    model = Expense

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Transaction updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.GET.get("next") or "/expenses/"


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    login_url = "users:login"
    template_name = "expenses/expense_confirm_delete.html"
    model = Expense

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Transaction deleted.")
        return "/expenses/"


class CategoryListView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "categories/category_list.html"

    def get(self, request):
        categories = Category.objects.filter(user=request.user)
        now = timezone.now()
        cat_stats = []
        for cat in categories:
            spent = Expense.objects.filter(
                user=request.user, category=cat,
                transaction_type=Expense.TransactionType.EXPENSE,
                date__year=now.year, date__month=now.month,
            ).aggregate(t=Sum("amount"))["t"] or 0
            cat_stats.append({"category": cat, "spent": spent})
        return render(request, self.template_name, {
            "cat_stats": cat_stats, "form": CategoryForm(), "currency": request.user.currency,
        })

    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            messages.success(request, f"Category '{cat.name}' created.")
            return redirect("expenses:categories")
        categories = Category.objects.filter(user=request.user)
        now = timezone.now()
        cat_stats = []
        for cat in categories:
            spent = Expense.objects.filter(
                user=request.user, category=cat,
                transaction_type=Expense.TransactionType.EXPENSE,
                date__year=now.year, date__month=now.month,
            ).aggregate(t=Sum("amount"))["t"] or 0
            cat_stats.append({"category": cat, "spent": spent})
        return render(request, self.template_name, {"cat_stats": cat_stats, "form": form})


class CategoryCreateView(LoginRequiredMixin, CreateView):
    login_url = "users:login"
    template_name = "categories/add_category.html"
    form_class = CategoryForm
    model = Category

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Category created.")
        return super().form_valid(form)

    def get_success_url(self):
        return "/expenses/categories/"


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "users:login"
    template_name = "categories/edit_category.html"
    form_class = CategoryForm
    model = Category

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Category updated.")
        return "/expenses/categories/"


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    login_url = "users:login"
    template_name = "expenses/category_confirm_delete.html"
    model = Category

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Category deleted.")
        return "/expenses/categories/"


class ReportsView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "reports/reports.html"

    def _date_range(self, request):
        now = timezone.now()
        period = request.GET.get("period", "month")
        if period == "week":
            start = (now - timedelta(days=7)).date()
            end = now.date()
        elif period == "30":
            start = (now - timedelta(days=30)).date()
            end = now.date()
        elif period == "custom":
            try:
                start = timezone.datetime.strptime(request.GET.get("start", ""), "%Y-%m-%d").date()
            except ValueError:
                start = now.replace(day=1).date()
            try:
                end = timezone.datetime.strptime(request.GET.get("end", ""), "%Y-%m-%d").date()
            except ValueError:
                end = now.date()
        else:
            start = now.replace(day=1).date()
            end = now.date()
        return start, end

    def get(self, request):
        start, end = self._date_range(request)
        qs = Expense.objects.filter(user=request.user, date__gte=start, date__lte=end).select_related("category")
        expenses = qs.filter(transaction_type=Expense.TransactionType.EXPENSE)
        income = qs.filter(transaction_type=Expense.TransactionType.INCOME)
        total_exp = expenses.aggregate(t=Sum("amount"))["t"] or 0
        total_inc = income.aggregate(t=Sum("amount"))["t"] or 0

        cat_data = list(expenses.values("category__name", "category__color").annotate(total=Sum("amount")).order_by("-total"))

        days = max((end - start).days, 1)
        avg_daily = total_exp / days if days > 0 else 0
        highest_cat = cat_data[0] if cat_data else None
        highest_txn = expenses.order_by("-amount").first()

        trend = {}
        current = start.replace(day=1)
        while current <= end:
            label = current.strftime("%b %Y")
            month_total = Expense.objects.filter(
                user=request.user, transaction_type=Expense.TransactionType.EXPENSE,
                date__year=current.year, date__month=current.month,
            ).aggregate(t=Sum("amount"))["t"] or 0
            trend[label] = float(month_total)
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return render(request, self.template_name, {
            "start": start, "end": end, "period": request.GET.get("period", "month"),
            "total_expenses": total_exp, "total_income": total_inc, "net": total_inc - total_exp,
            "avg_daily": avg_daily, "highest_cat": highest_cat, "highest_txn": highest_txn,
            "category_data": cat_data, "trend": trend, "transactions": qs[:50],
            "currency": request.user.currency,
        })

    def post(self, request):
        start, end = self._date_range(request)
        qs = Expense.objects.filter(user=request.user, date__gte=start, date__lte=end).select_related("category")
        export_type = request.POST.get("export_type", "csv")

        if export_type == "pdf":
            return self._export_pdf(qs, start, end, request.user)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="isiro_report.csv"'
        writer = csv.writer(response)
        writer.writerow(["Date", "Type", "Category", "Description", "Amount", "Payment Method", "Status"])
        for t in qs:
            writer.writerow([t.date, t.get_transaction_type_display(), t.category.name if t.category else "", t.description, t.amount, t.get_payment_method_display(), t.get_status_display()])
        return response

    def _export_pdf(self, qs, start, end, user):
        from django.http import HttpResponse as HR
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        except ImportError:
            messages.error(self.request, "PDF export requires reportlab.")
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="isiro_report.csv"'
            writer = csv.writer(response)
            writer.writerow(["Date", "Type", "Category", "Description", "Amount"])
            for t in qs:
                writer.writerow([t.date, t.get_transaction_type_display(), t.category.name if t.category else "", t.description, t.amount])
            return response

        response = HR(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="isiro_report.pdf"'
        doc = SimpleDocTemplate(response, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        elements.append(Paragraph("Isiro Financial Report", styles["Title"]))
        elements.append(Paragraph(f"User: {user.full_name or user.email}<br/>Period: {start} to {end}", styles["Normal"]))
        elements.append(Spacer(1, 20))
        data = [["Date", "Type", "Category", "Description", "Amount"]]
        for t in qs[:100]:
            data.append([str(t.date), t.get_transaction_type_display(), t.category.name if t.category else "—", t.description[:40], str(t.amount)])
        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
        ]))
        elements.append(table)
        doc.build(elements)
        return response
