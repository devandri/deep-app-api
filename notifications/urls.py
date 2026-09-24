from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("notify/", views.notify_user, name="notify-user"),
    path("broadcast/", views.broadcast, name="broadcast"),
]
