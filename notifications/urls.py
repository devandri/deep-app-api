from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("notify/", views.notify_user, name="notify-user"),
    path("broadcast/", views.broadcast, name="broadcast"),
    path("notifications-list/", views.list_notifications, name="list-notifications"),
    path("notifications-read-all/", views.mark_all_read_old, name="notifications-read-all"),
    path("read-all/", views.mark_all_read, name="notifications-read-all"),
    path("<int:pk>/read/", views.mark_read, name="notification-mark-read"),
    path("", views.notifications_list, name="notifications-list"),
    path("summary/", views.notification_summary, name="notifications-summary"),
]
