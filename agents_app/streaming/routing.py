"""
Django Channels routing configuration.

Maps WebSocket URLs to consumers.
"""

from django.urls import re_path
from agents_app.streaming.consumers import StreamingConsumer

websocket_urlpatterns = [
    re_path(r"ws/stream/(?P<session_id>\d+)/$", StreamingConsumer.as_asgi()),
]
