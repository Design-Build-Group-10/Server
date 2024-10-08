"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from apps.robot.routing import websocket_urlpatterns
from apps.robot.routing import websocket_urlpatterns as robot_camera_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket": AuthMiddlewareStack(
    #     URLRouter([
    #         path('ws/camera/', CameraConsumer.as_asgi()),
    #     ])
    # ),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns + robot_camera_websocket_urlpatterns)
    ),
})
