from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from rest_framework.response import Response
from .utils import send_notification_to_user, broadcast_notification
from .models import Notification
import json

User = get_user_model()

def serialize(n):
    return {
        "id": n.id,
        "type": n.type,
        "title": n.title,
        "body": n.body,
        "data": n.data,
        "isRead": n.is_read,
        "createdAt": n.created_at.isoformat(),
    }

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

# @login_required
@require_GET
def list_notifications(request):
    qs = Notification.objects.filter(user=request.user).order_by("-created_at")[:50]
    data = [
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "body": n.body,
            "data": n.data,
            "isRead": n.is_read,
            "createdAt": n.created_at.isoformat(),
        }
        for n in qs
    ]
    return JsonResponse({"results": data})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    """GET /api/notifications/?unread=1&limit=50"""
    qs = Notification.objects.filter(user=request.user)

    if request.query_params.get("unread") in ("1", "true"):
        qs = qs.filter(is_read=False)

    limit = min(int(request.query_params.get("limit", 50)), 200)
    qs = qs.order_by("-created_at")[:limit]
    
    return Response([serialize(n) for n in qs])

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_summary(request):
    """GET /api/notifications/summary/ -> { unread, total }"""
    qs = Notification.objects.filter(user=request.user)
    return Response({
        "unread": qs.filter(is_read=False).count(),
        "total": qs.count()
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_read(request, pk):
    """POST /api/notifications/<id>/read/"""
    updated = Notification.objects.filter(
        id=pk, user=request.user, is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return Response({"status": "ok", "updated": updated}) 

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """POST /api/notifications/read-all"""
    updated = Notification.objects.filter(
        user=request.user, is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return Response({ "status": "ok", "updated": updated })

@login_required
@csrf_exempt
@require_POST
def mark_all_read_old(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"status": "ok"})