"""URL routes for income tracking.

Income uses the Expense model with transaction_type='income'.
"""

from django.urls import path
from .views_income import IncomeCreateView, IncomeDetailView, IncomeListView

app_name = "income"

urlpatterns = [
    path("", IncomeListView.as_view(), name="income_list"),
    path("add/", IncomeCreateView.as_view(), name="income_add"),
    path("<int:pk>/", IncomeDetailView.as_view(), name="income_detail"),
]
