import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

def send_notification_to_user(user_id, title, body, type_="info", extra=None):
    """
    Push a notification to a single connected user.
    Safe to call from sync code (views, signals, celery tasks).
    """
    
    from .models import Notification
    
    # 1) Persist - so the user gets it even if offline
    n = Notification.objects.create(
        user_id=user_id,
        title=title,
        body=body,
        type=type_,
        data=extra or {}
    )
    
    # 2) Push live (no-op if the user has no open socket)
    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.warning("No channel layer - cannot send notification")
        return
    
    payload = {
        "id": n.id,
        "title": title,
        "body": body,
        "type": type_,
        # **(extra or {}),
        "data":n.data,
        "createdAt": n.created_at.isoformat(),
    }
    
    async_to_sync(channel_layer.group_send) (
        f"user_{user_id}",
        {
            "type": "notify",   # consumer's notify() method
            "payload": payload,
        }
    )
    
    # logger.info(
    #     "Notification queued | to_user_id=%s | type=%s | title=%r",
    #     user_id, type_, title,
    # )
    logger.info(
        "Notification #%s sent to user user=%s",
        n.id, user_id,
    )
    return n
    
def send_notification_to_room(room, title, body, type_="info", extra=None):
    """
    Broadcast to everyone in a room group
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send) (
        room,
        {
            "type": "room_event",
            "event": "notification",
            "data": {
                "title": title,
                "body": body,
                "type": type_,
                **(extra or {}),
            },
        },
    )
    
def broadcast_notification(title, body, type_="info", extra=None):
    """
    Broadcast to all connected clients (system-wide).
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send ) (
        "broadcast",
        {
            "type": "notify",
            "payload": {
                "title": title,
                "body": body,
                "type": type_,
                **(extra or {})
            }
        }
    )
    