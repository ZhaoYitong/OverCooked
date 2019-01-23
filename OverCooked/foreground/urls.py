from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^ordering/$', views.ordering, name='ordering'),
    url(r'^ordered/$', views.ordered, name='ordered'),
    url(r'^food/$', views.food, name='food'),
    url(r'^update_food/$', views.update_food, name='update_food'),
    url(r'^sale/$', views.sale, name='sale'),
]
