"""Models for the imports app."""

from django.conf import settings
from django.db import models


class ImportedFile(models.Model):
    class FileType(models.TextChoices):
        PDF = "pdf", "PDF"
        CSV = "csv", "CSV"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="imported_files")
    file = models.FileField(upload_to="imports/", blank=True, null=True)
    file_type = models.CharField(max_length=5, choices=FileType.choices)
    bank_name = models.CharField(max_length=100, blank=True)
    file_name = models.CharField(max_length=255)
    row_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} ({self.get_file_type_display()})"


class ImportTransaction(models.Model):
    imported_file = models.ForeignKey(ImportedFile, on_delete=models.CASCADE, related_name="transactions")
    date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    category = models.CharField(max_length=80, blank=True)
    transaction_type = models.CharField(max_length=10, default="expense")
    confidence_score = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.date} — {self.description} — {self.amount}"


ImportBatch = ImportedFile
