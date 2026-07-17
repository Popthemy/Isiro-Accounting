"""Views for the budgets app — list, create, detail, edit, delete."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DeleteView

from expenses.models import Expense

from .forms import BudgetForm
from .models import Budget


class BudgetListView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "budgets/budget_list.html"

    def get(self, request):
        budgets = Budget.objects.filter(user=request.user).select_related("category")
        return render(request, self.template_name, {"budgets": budgets, "currency": request.user.currency})


class BudgetCreateView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "budgets/add_budget.html"

    def get(self, request):
        return render(request, self.template_name, {"form": BudgetForm(user=request.user)})

    def post(self, request):
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, f"Budget '{budget.name}' created.")
            return redirect("budgets:list")
        return render(request, self.template_name, {"form": form})


class BudgetDetailView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "budgets/budget_detail.html"

    def get(self, request, pk):
        budget = get_object_or_404(Budget.objects.select_related("category"), pk=pk, user=request.user)
        transactions = Expense.objects.filter(
            user=request.user, category=budget.category,
            transaction_type=Expense.TransactionType.EXPENSE,
            date__gte=budget.start_date, date__lte=budget.end_date,
        ).order_by("-date")
        return render(request, self.template_name, {"budget": budget, "transactions": transactions, "currency": request.user.currency})


class BudgetEditView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "budgets/edit_budget.html"

    def get(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        return render(request, self.template_name, {"form": BudgetForm(instance=budget, user=request.user), "budget": budget})

    def post(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Budget updated.")
            return redirect("budgets:list")
        return render(request, self.template_name, {"form": form, "budget": budget})


class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    login_url = "users:login"
    template_name = "budgets/budget_confirm_delete.html"
    model = Budget

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Budget deleted.")
        return "/budgets/"
