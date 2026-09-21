from django.urls import re_path
# from . import consumers
from notifications.v2 import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/notifications/$",
        # consumers.NotificationConsumer.as_asgi()
        consumers.NotificationConsumerV2.as_asgi()
    ),
]