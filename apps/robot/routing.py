from django.urls import re_path

from apps.robot.consumers import CameraConsumer

websocket_urlpatterns = [
    re_path(r'ws/camera/$', CameraConsumer.as_asgi()),
]
