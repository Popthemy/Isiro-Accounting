from django.urls import path
from .views import BudgetCreateView, BudgetDeleteView, BudgetDetailView, BudgetEditView, BudgetListView

app_name = "budgets"

urlpatterns = [
    path("", BudgetListView.as_view(), name="list"),
    path("add/", BudgetCreateView.as_view(), name="add"),
    path("<int:pk>/", BudgetDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", BudgetEditView.as_view(), name="edit"),
    path("<int:pk>/delete/", BudgetDeleteView.as_view(), name="delete"),
]
