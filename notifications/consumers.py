import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            "message": "Hello Vue! Realtime connected."
        }))
        
    async def disconnect(self, close_code):
        print("WebSocket disconnected")

    async def receive(self, text_data):
        logger.info(f"Received from client: {text_data}")
        data = json.loads(text_data)
        msg = data.get("message", "No Message")
        await self.send(text_data=json.dumps({
            "message": f"You said: {msg}"
        }))