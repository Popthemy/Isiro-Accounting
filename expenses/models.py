"""Models for the expenses app.

Two models drive the whole platform:

* ``Category``  — a user-defined or default spending category.
* ``Expense``   — a single income or expense transaction.
"""

from django.conf import settings
from django.db import models


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
    attachment = models.FileField(upload_to="attachments/", blank=True, null=True)
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

    def __str__(self) -> str:
        return f"{self.get_transaction_type_display()} {self.amount} — {self.description}"

    @property
    def signed_amount(self):
        """Negative for expenses, positive for income."""
        return -self.amount if self.transaction_type == self.TransactionType.EXPENSE else self.amount
