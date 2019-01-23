from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import kitchen.routing
import foreground.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            kitchen.routing.websocket_urlpatterns +
            foreground.routing.websocket_urlpatterns
        )
    ),
})
