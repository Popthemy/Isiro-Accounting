from django.contrib import admin
from .models import ImportedFile, ImportTransaction

@admin.register(ImportedFile)
class ImportedFileAdmin(admin.ModelAdmin):
    list_display = ("user", "file_name", "file_type", "bank_name", "row_count", "status", "uploaded_at")
    list_filter = ("file_type", "status")
    search_fields = ("file_name", "bank_name", "user__email")
    date_hierarchy = "uploaded_at"

@admin.register(ImportTransaction)
class ImportTransactionAdmin(admin.ModelAdmin):
    list_display = ("imported_file", "date", "description", "amount", "transaction_type", "confidence_score")
    list_filter = ("transaction_type",)
    search_fields = ("description",)
