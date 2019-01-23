from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^distribution/$', views.distribution, name='distribution'),
    url(r'^prepare/$', views.prepare, name='prepare'),
    url(r'^finish/$', views.finish, name='finish'),
]
