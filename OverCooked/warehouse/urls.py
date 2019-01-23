from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^entry/$', views.entry, name='entry'),
    url(r'^inventory/$', views.inventory, name='inventory'),
    url(r'^scrap/$', views.scrap, name='scrap'),
    url(r'^query/$', views.query, name='query'),
    url(r'^purchase/$', views.purchase, name='purchase'),
    url(r'^purchase_confirm/$', views.purchase_confirm, name='purchase_confirm'),
    url(r'^purchased/$', views.purchased, name='purchased'),
    url(r'^supplier/$', views.supplier, name='supplier'),
    url(r'^del_supplier/$', views.del_supplier, name='del_supplier'),
    url(r'^delivery/$', views.delivery, name='delivery'),
]
