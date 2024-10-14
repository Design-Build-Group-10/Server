from django.urls import re_path

from apps.robot.consumers import CameraConsumer, TransmitConsumer

websocket_urlpatterns = [
    re_path(r'ws/camera/(?P<serial_number>[^/]+)$', CameraConsumer.as_asgi()),
    re_path(r'ws/transmit/(?P<serial_number>[^/]+)$', TransmitConsumer.as_asgi()),
]
