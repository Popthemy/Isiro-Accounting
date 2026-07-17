"""Views for the core app — activity log viewing."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from .models import ActivityLog


@method_decorator(staff_member_required, name="dispatch")
class ActivityLogView(View):
    template_name = "admin/activity_logs.html"

    def get(self, request):
        logs = ActivityLog.objects.select_related("user").all()[:200]
        return render(request, self.template_name, {"logs": logs})
