import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)

class NotificationConsumerV2(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = None
        self.user_group = None
        self.joined_rooms = set()
        # Get token from query string: ws://.../ws/nitifications/?token=xxx
        query = parse_qs(self.scope["query_string"].decode())
        token = query.get("token", [None])[0]
        
        logger.info(
            "WS connect attempt | ip=%s | has_token=%s | channel=%s",
            self.scope.get('client', ("unknown", 0))[0], bool(token), self.channel_name
        )
        
        self.user = await self.get_user_from_token(token)
        if not self.user:
            logger.warning(
                "WS auth FAILED | ip=%s | channel=%s | reason=invalid_or_missing_token", self.scope.get('client', ("unknown", 0))[0], self.channel_name
            )
            await self.close(code=401)
            return
        
        self.user_group = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.channel_layer.group_add("broadcast", self.channel_name)
        await self.accept()
        
        logger.info(
            "WS CONNECTED | user_id=%s | username=%s | ip=%s | channel=%s", self.user.id, getattr(self.user, "username", "?"), self.scope.get('client', ("unknown", 0))[0], self.channel_name
        )

        await self.send_json({
            "event": "connect",
            "data": { "userId": self.user.id }
        })
        
    async def disconnect(self, close_code):
        # if hasattr(self, "user_group"):
        #     await self.channel_layer.group_discard(self.user_group, self.channel_name)
        #     await self.channel_layer.group_discard("broadcast", self.channel_name)
        # leave dynamic rooms
        for room in getattr(self, "joined_rooms", set()):
            try:
                await self.channel_layer.group_discard(room, self.channel_name)
            except Exception:
                logger.exception("WS leave-room failed on disconnect | room=%s", room)
                
        if getattr(self, "user_group", None):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        await self.channel_layer.group_discard("broadcast", self.channel_name)
            
    async def receive(self, text_data):
        user_id = getattr(self.user, "id", None)
        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            logger.warning("WS recv INVALID JSON | user_id=%s", user_id)
            return
        
        event = payload.get("event")
        data = payload.get("data", {}) or {}
        
        logger.debug("WS recv | user_id=%s | event=%s | data=%s", user_id, event, data)

        if event == "join":
            room = data.get("room")
            if not room:
                return
            await self.channel_layer.group_add(room, self.channel_name)
            self.joined_rooms.add(room)
            logger.info("WS JOINED | user_id=%s | room=%s", user_id, room)
                
        elif event == "leave":
            room = data.get("room")
            if not room:
                return
            await self.channel_layer.group_discard(room, self.channel_name)
            self.joined_rooms.discard(room)
            logger.info("WS LEFT | user_id=%s | room=%s", user_id, room)
                
        elif event == "ping":
            await self.send_json({ "event": "pong", "data": data})
            
        elif event == "typing":
            room = data.get("room")
            if not room or not self.user:
                return
            await self.channel_layer.group_send(room, {
                "type": "room_event",
                "event": "typing",
                "data": {
                    "room": room,
                    "userId": self.user.id,
                    "username": getattr(self.user, "username", f"user_{self.user.id}"),
                    "isTyping": bool(data.get("isTyping")),
                },
            })
            
        elif event == "chat_message":
            room = data.get("room")
            message = (data.get("message") or "").strip()
            if not room or not message:
                return
            # length guard
            if len(message) > 2000:
                message = message[:2000]

            await self.channel_layer.group_send(room, {
                "type": "room_event",
                "event": "chat_message",
                "data": {
                    "room": room,
                    "userId": self.user.id,
                    "username": getattr(self.user, "username", f"user_{self.user.id}"),
                    "message": message,
                    "ts": int(__import__("time").time() * 1000),
                },
            })
            
        else:
            logger.warning("WS UNKNOWN event | user_id=%s | event=%r", user_id, event)
            
    # group message handlers
    async def notify(self, event):
        """Fired when someone does group_send(type='notify', ...)"""
        await self.send_json({
            "event": "notification",
            "data": event["payload"],
        })
        
    async def user_status(self, event):
        await self.send_json({
            "event": event["status"], # "user_online" / "user_offline"
            "data": event["payload"]
        })
        
    # Helpers
    async def send_json(self, obj):
        await self.send(text_data=json.dumps(obj))
        
    @database_sync_to_async
    def get_user_from_token(self, token):
        if not token:
            return None
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth import get_user_model
        try:
            access = AccessToken(token)
            return get_user_model().objects.get(id=access["user_id"])
        except Exception:
            return None