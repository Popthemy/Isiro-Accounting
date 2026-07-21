"""Forms for expense and category management."""

from django import forms

from .models import Category, Expense, Wallet


class WalletForm(forms.ModelForm):
    """Create or edit a wallet account."""

    class Meta:
        model = Wallet
        fields = ("name", "account_type", "opening_balance", "currency", "description", "is_active")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "GTBank"}),
            "account_type": forms.Select(attrs={"class": "form-input"}),
            "opening_balance": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}),
            "currency": forms.TextInput(attrs={"class": "form-input", "placeholder": "USD"}),
            "description": forms.TextInput(attrs={"class": "form-input", "placeholder": "Optional notes"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_opening_balance(self):
        opening_balance = self.cleaned_data.get("opening_balance")
        if opening_balance is not None and opening_balance < 0:
            raise forms.ValidationError("Opening balance cannot be negative.")
        return opening_balance


class ExpenseForm(forms.ModelForm):
    """Create or edit a single transaction."""

    class Meta:
        model = Expense
        fields = ("wallet", "amount", "date", "category", "description",
                  "transaction_type", "payment_method", "merchant_name",
                  "location", "notes", "attachment")
        widgets = {
            "wallet": forms.Select(attrs={"class": "form-input"}),
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
        self.request_user = user
        if user:
            self.fields["category"].queryset = Category.objects.filter(user=user)
            self.fields["wallet"].queryset = Wallet.objects.filter(user=user, is_active=True)
            self.fields["wallet"].empty_label = "Select Wallet"

    def clean_wallet(self):
        wallet = self.cleaned_data.get("wallet")

        if not wallet:
            return wallet

        instance_user = getattr(self.instance, "user", None)

        if instance_user:
            if wallet.user != instance_user:
                raise forms.ValidationError("Select a wallet for this user.")
        elif wallet.user != self.request_user:
            raise forms.ValidationError("Select a wallet for this user.")

        return wallet


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
