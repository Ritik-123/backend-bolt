# daphne -b 0.0.0.0 -p 8000 backend_bolt.asgi:application

import os, django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_bolt.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# django_asgi_app = get_asgi_application()

from users.router import websocket_urlpatterns
# import users.router



application= ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': AuthMiddlewareStack(
            URLRouter(
                # users.router.websocket_urlpatterns
                websocket_urlpatterns
                )
            ) 
    }
)

# application = get_asgi_application()
# application= ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': AllowedHostsOriginValidator(
#         AuthMiddlewareStack(
#             URLRouter(
#                 websocket_urlpatterns
#             )
#         )
#     ),
# })