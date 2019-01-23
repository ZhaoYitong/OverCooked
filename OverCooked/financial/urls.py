from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^procurementList_Cost/$', views.procurementList_Cost, name='procurementList_Cost'),
    url(r'^financialSalary/$', views.financialSalary, name='financialSalary'),
    url(r'^daily/$', views.daily, name='daily'),
    url(r'^financialStatement/$', views.financialStatement, name='financialStatement'),

]

