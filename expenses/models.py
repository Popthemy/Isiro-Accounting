"""Models for the expenses app.

Two models drive the whole platform:

* ``Category``  — a user-defined or default spending category.
* ``Expense``   — a single income or expense transaction.
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F


class Wallet(models.Model):
    """A user's wallet or account used as the balance source for transactions."""

    class AccountType(models.TextChoices):
        CASH = "cash", "Cash"
        BANK = "bank", "Bank Account"
        MOBILE = "mobile", "Mobile Money"
        CARD = "card", "Credit Card"
        SAVINGS = "savings", "Savings"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallets",
    )
    name = models.CharField(max_length=120)
    account_type = models.CharField(
        max_length=12,
        choices=AccountType.choices,
        default=AccountType.CASH,
    )
    opening_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="USD")
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"], name="unique_wallet_name_per_user"),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self):
        super().clean()
        if self.opening_balance < 0:
            raise ValidationError(
                {"opening_balance": "Opening balance cannot be negative."})

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.pk is None:
            self.current_balance = self.opening_balance
        super().save(*args, **kwargs)


class Category(models.Model):
    """A spending or income category with icon and colour."""

    name = models.CharField(max_length=80)
    icon = models.CharField(max_length=50, default="fa-tag")
    color = models.CharField(max_length=20, default="#6B7280")
    is_default = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user"], name="unique_category_per_user",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Expense(models.Model):
    """A single transaction — either an expense or income."""

    @staticmethod
    def _signed_amount(amount, transaction_type):
        amount = Decimal(amount)
        return amount if transaction_type == Expense.TransactionType.INCOME else -amount

    @staticmethod
    @transaction.atomic
    def _adjust_wallet_balance(wallet_id, delta):
        Wallet.objects.filter(pk=wallet_id).update(
            current_balance=F("current_balance") + delta)

    class TransactionType(models.TextChoices):
        EXPENSE = "expense", "Expense"
        INCOME = "income", "Income"

    class Source(models.TextChoices):
        MANUAL = "manual", "Manual"
        PDF = "pdf", "PDF Import"
        CSV = "csv", "CSV Import"
        OCR = "ocr", "OCR Import"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        BANK = "bank", "Bank Transfer"
        MOBILE = "mobile", "Mobile Money"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="expenses",
    )
    description = models.CharField(max_length=255, blank=True)
    transaction_type = models.CharField(
        max_length=10, choices=TransactionType.choices, default=TransactionType.EXPENSE,
    )
    payment_method = models.CharField(
        max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.CASH,
    )
    source = models.CharField(
        max_length=10, choices=Source.choices, default=Source.MANUAL,
    )
    attachment = models.FileField(
        upload_to="attachments/", blank=True, null=True)
    merchant_name = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.COMPLETED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "transaction_type"]),
        ]

    @transaction.atomic
    def save(self, *args, **kwargs):
        previous = None
        if self.pk:
            previous = Expense.objects.only(
                "wallet_id", "amount", "transaction_type").get(pk=self.pk)

        super().save(*args, **kwargs)

        if previous:
            self._adjust_wallet_balance(
                previous.wallet_id, -self._signed_amount(previous.amount, previous.transaction_type))

        if self.wallet_id:
            self._adjust_wallet_balance(self.wallet_id, self._signed_amount(
                self.amount, self.transaction_type))

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.wallet_id:
            self._adjust_wallet_balance(
                self.wallet_id, -self._signed_amount(self.amount, self.transaction_type))
        return super().delete(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.get_transaction_type_display()} {self.amount} — {self.description}"

    @property
    def signed_amount(self):
        """Negative for expenses, positive for income."""
        return -self.amount if self.transaction_type == self.TransactionType.EXPENSE else self.amount
