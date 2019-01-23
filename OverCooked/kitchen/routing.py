from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/kitchen/distribution/$', consumers.DistributeConsumer),
    url(r'^ws/kitchen/prepare/$', consumers.PrepareConsumer),
]