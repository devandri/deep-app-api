from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .utils import send_notification_to_user, broadcast_notification
import json

User = get_user_model()

# @login_required
@csrf_exempt
def notify_user(request):
    """POST /api/notify/ { userId, title, body, type }"""
    data = json.loads(request.body)
    target = get_object_or_404(User, id=data["userId"])
    send_notification_to_user(
        user_id=target.id,
        title=data.get("title", "New notification"),
        body=data.get("body", ""),
        type_=data.get("type", "info"),
    )
    return JsonResponse({"status": "sent"})

@csrf_exempt
def broadcast(request):
    """POST /api/broadcast/ { title, body }"""
    data = json.loads(request.body)
    broadcast_notification(
        title=data.get("title", "Announcement"),
        body=data.get("body", ""),
        type_="info",
    )
    return JsonResponse({"status": "broadcasted"})
