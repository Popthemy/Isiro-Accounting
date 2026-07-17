"""Views for income tracking.

Income uses the Expense model with transaction_type='income'.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import ExpenseForm
from .models import Expense


class IncomeListView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "income/income_list.html"

    def get(self, request):
        incomes = Expense.objects.filter(
            user=request.user,
            transaction_type=Expense.TransactionType.INCOME,
        ).select_related("category")
        return render(request, self.template_name, {"incomes": incomes, "currency": request.user.currency})


class IncomeCreateView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "income/add_income.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ExpenseForm(user=request.user)})

    def post(self, request):
        data = request.POST.copy()
        data["transaction_type"] = Expense.TransactionType.INCOME
        form = ExpenseForm(data, request.FILES, user=request.user )
        print(f" valid: {form.is_valid()} Form data: {request.POST}")  # Debugging line

        if form.is_valid():
            print(f"Form is valid. Cleaned data: {form.cleaned_data}")  # Debugging line
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, "Income added successfully.")
            return redirect("income:income_list")
        print(f"errors, {form.errors}")
        # messages.error(self.request, f"error occured: {form.errors}")
        
        return render(request, self.template_name, {"form": form})


class IncomeDetailView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "income/income_detail.html"

    def get(self, request, pk):
        income = get_object_or_404(Expense, pk=pk, user=request.user, transaction_type=Expense.TransactionType.INCOME)
        return render(request, self.template_name, {"income": income, "currency": request.user.currency})
