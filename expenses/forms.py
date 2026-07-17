"""Forms for expense and category management."""

from django import forms

from .models import Category, Expense


class ExpenseForm(forms.ModelForm):
    """Create or edit a single transaction."""

    class Meta:
        model = Expense
        fields = ("amount", "date", "category", "description",
                  "transaction_type", "payment_method", "merchant_name",
                  "location", "notes", "attachment")
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "category": forms.Select(attrs={"class": "form-input"}),
            "description": forms.TextInput(attrs={"class": "form-input", "placeholder": "Lunch at restaurant"}),
            "transaction_type": forms.Select(attrs={"class": "form-input"}),
            "payment_method": forms.Select(attrs={"class": "form-input"}),
            "merchant_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Store name (optional)"}),
            "location": forms.TextInput(attrs={"class": "form-input", "placeholder": "City or address (optional)"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Additional notes (optional)"}),
            "attachment": forms.FileInput(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["category"].queryset = Category.objects.filter(user=user)


class CategoryForm(forms.ModelForm):
    """Create or edit a custom category."""

    class Meta:
        model = Category
        fields = ("name", "icon", "color")
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "Groceries",
            }),
            "icon": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "fa-shopping-cart",
            }),
            "color": forms.TextInput(attrs={
                "class": "form-input", "type": "color",
            }),
        }
