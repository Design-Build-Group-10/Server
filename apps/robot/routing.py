from django.urls import re_path

from apps.robot.consumers import CameraConsumer, CameraHandledConsumer

websocket_urlpatterns = [
    re_path(r'ws/camera/(?P<serial_number>[^/]+)$', CameraConsumer.as_asgi()),
    re_path(r'ws/camera/handled/(?P<serial_number>[^/]+)/$', CameraHandledConsumer.as_asgi()),
]
