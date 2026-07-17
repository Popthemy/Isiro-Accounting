"""Forms for budget creation and editing."""

from django import forms

from expenses.models import Category

from .models import Budget


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ("name", "category", "amount_limit", "period_type",
                  "start_date", "end_date", "alert_percentage", "is_active")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Monthly Food Budget"}),
            "category": forms.Select(attrs={"class": "form-input"}),
            "amount_limit": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "500.00"}),
            "period_type": forms.Select(attrs={"class": "form-input"}),
            "start_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "alert_percentage": forms.NumberInput(attrs={"class": "form-input", "min": "1", "max": "100", "placeholder": "80"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["category"].queryset = Category.objects.filter(user=user)
