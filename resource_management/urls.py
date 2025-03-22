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
from django.urls import path
from core.views import (
    RegisterView, login_view, dashboard, LogoutView,
    ResourceListView, ResourceCreateView, ResourceUpdateView,
    ResourceDeleteView, ResourceDetailView, ProfileUpdateView,
    change_password, ResourceExportView, ResourceImportView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Resource Management URLs
    path('resources/', ResourceListView.as_view(), name='resource_list'),
    path('resources/add/', ResourceCreateView.as_view(), name='resource_create'),
    path('resources/<int:pk>/', ResourceDetailView.as_view(), name='resource_detail'),
    path('resources/<int:pk>/edit/', ResourceUpdateView.as_view(), name='resource_update'),
    path('resources/<int:pk>/delete/', ResourceDeleteView.as_view(), name='resource_delete'),
    
    # Resource Import/Export URLs
    path("resources/export/", ResourceExportView.as_view(), name="resource_export"),
    path("resources/import/", ResourceImportView.as_view(), name="resource_import"),
    
    # Profile Management URLs
    path('profile/', ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/password/', change_password, name='change_password'),
]
