from django.contrib import admin
from .models import Notification

# Register your models here.

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "title", "is_read", "created_at", "read_at")
    list_filter = ("type", "is_read", "created_at", "read_at")
    search_fields = ("title", "body", "user__username")
    raw_id_fields = ("user",)