from django.urls import path
from .views import ActivityLogView

app_name = "core"

urlpatterns = [
    path("admin/activity-logs/", ActivityLogView.as_view(), name="activity_logs"),
]
