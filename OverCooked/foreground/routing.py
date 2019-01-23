from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/foreground/order/$', consumers.OrderConsumer),
    url(r'^ws/foreground/statics/$', consumers.StaticsConsumer),
]
