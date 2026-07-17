from django.urls import path
from .views import ImportConfirmView, ImportHistoryView, ImportUploadView

app_name = "imports"

urlpatterns = [
    path("", ImportUploadView.as_view(), name="upload"),
    path("confirm/", ImportConfirmView.as_view(), name="confirm"),
    path("history/", ImportHistoryView.as_view(), name="history"),
]
