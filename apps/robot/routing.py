from django.urls import re_path

from apps.robot.consumers import CameraConsumer

websocket_urlpatterns = [
    re_path(r'ws/camera/(?P<serial_number>[^/]+)$', CameraConsumer.as_asgi()),
]
