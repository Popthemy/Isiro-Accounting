"""Views for the notifications app."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from .models import Notification


class NotificationListView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "notifications/notification_list.html"

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        unread = notifications.filter(is_read=False).count()
        return render(request, self.template_name, {"notifications": notifications, "unread_count": unread})


class NotificationMarkReadView(LoginRequiredMixin, View):
    login_url = "users:login"

    def post(self, request, pk):
        try:
            n = Notification.objects.get(pk=pk, user=request.user)
            n.is_read = True
            n.save()
        except Notification.DoesNotExist:
            pass
        return redirect("notifications:list")


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    login_url = "users:login"

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect("notifications:list")


class NotificationDropdownView(LoginRequiredMixin, View):
    login_url = "users:login"

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)[:5]
        unread = Notification.objects.filter(user=request.user, is_read=False).count()
        data = {
            "unread": unread,
            "notifications": [
                {"id": n.id, "title": n.title, "message": n.message, "type": n.type,
                 "is_read": n.is_read, "created_at": n.created_at.strftime("%d %b, %H:%M")}
                for n in notifications
            ],
        }
        return JsonResponse(data)
