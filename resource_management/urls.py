"""
URL configuration for resource_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import (
    RegisterView, 
    LoginView,
    LogoutView,
    DashboardView,
    ProfileUpdateView,
    change_password,
    
    # Device Arrival views
    DeviceArrivalListView,
    DeviceArrivalCreateView, 
    DeviceArrivalUpdateView,
    DeviceArrivalDeleteView,
    DeviceArrivalExportView,
    DeviceArrivalImportView,
    
    # Device Delivery views
    DeviceDeliveryListView,
    DeviceDeliveryCreateView,
    DeviceDeliveryUpdateView,
    DeviceDeliveryDeleteView,
    DeviceDeliveryExportView,
    DeviceDeliveryImportView,
    
    # Device Security Status views
    DeviceSecurityStatusListView,
    DeviceSecurityStatusCreateView,
    DeviceSecurityStatusUpdateView,
    DeviceSecurityStatusDeleteView,
    DeviceSecurityStatusExportView,
    DeviceSecurityStatusImportView,
    
    # Dashboard Status view
    DashboardStatusView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),
    path('dashboard/status/', DashboardStatusView.as_view(), name='dashboard_status'),
    
    # Profile
    path('profile/', ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/change-password/', change_password, name='change_password'),
    
    # Device Arrival URLs
    path('device-arrivals/', DeviceArrivalListView.as_view(), name='device_arrival_list'),
    path('device-arrivals/add/', DeviceArrivalCreateView.as_view(), name='device_arrival_create'),
    path('device-arrivals/<int:pk>/edit/', DeviceArrivalUpdateView.as_view(), name='device_arrival_update'),
    path('device-arrivals/<int:pk>/delete/', DeviceArrivalDeleteView.as_view(), name='device_arrival_delete'),
    path('device-arrivals/export/', DeviceArrivalExportView.as_view(), name='device_arrival_export'),
    path('device-arrivals/import/', DeviceArrivalImportView.as_view(), name='device_arrival_import'),
    
    # Device Delivery URLs
    path('device-deliveries/', DeviceDeliveryListView.as_view(), name='device_delivery_list'),
    path('device-deliveries/add/', DeviceDeliveryCreateView.as_view(), name='device_delivery_create'),
    path('device-deliveries/<int:pk>/edit/', DeviceDeliveryUpdateView.as_view(), name='device_delivery_update'),
    path('device-deliveries/<int:pk>/delete/', DeviceDeliveryDeleteView.as_view(), name='device_delivery_delete'),
    path('device-deliveries/export/', DeviceDeliveryExportView.as_view(), name='device_delivery_export'),
    path('device-deliveries/import/', DeviceDeliveryImportView.as_view(), name='device_delivery_import'),
    
    # Device Security Status URLs
    path('device-security-status/', DeviceSecurityStatusListView.as_view(), name='device_security_status_list'),
    path('device-security-status/add/', DeviceSecurityStatusCreateView.as_view(), name='device_security_status_create'),
    path('device-security-status/<int:pk>/edit/', DeviceSecurityStatusUpdateView.as_view(), name='device_security_status_update'),
    path('device-security-status/<int:pk>/delete/', DeviceSecurityStatusDeleteView.as_view(), name='device_security_status_delete'),
    path('device-security-status/export/', DeviceSecurityStatusExportView.as_view(), name='device_security_status_export'),
    path('device-security-status/import/', DeviceSecurityStatusImportView.as_view(), name='device_security_status_import'),
]

# 添加静态文件URL配置
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
