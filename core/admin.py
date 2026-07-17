from django.contrib import admin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("action", "module", "user", "status", "ip_address", "created_at")
    list_filter = ("module", "status")
    search_fields = ("action", "description", "user__email")
    date_hierarchy = "created_at"
