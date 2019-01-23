from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    url(r'^employeeInfo/$', views.employeeInfo, name='employeeInfo'), # 基本信息录入
    url(r'^employeeBasicInfo/$', views.employeeBasicInfo, name='employeeBasicInfo'),
    url(r'^employeeDistribute/$', views.employeeDistribute, name='employeeDistribute'),
    url(r'^employeePerform/$', views.employeePerform, name='employeePerform'),
    url(r'^employeeSalary/$', views.employeeSalary, name='employeeSalary'),
    url(r'^deleteEvent/$', views.deleteEvent, name='deleteEvent'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # file upload
