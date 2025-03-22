from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Resource5G

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'groups')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('email', 'phone')}),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2'),
        }),
    )

@admin.register(Resource5G)
class Resource5GAdmin(admin.ModelAdmin):
    list_display = ('name', 'resource_type', 'location', 'quantity', 'status', 'user', 'created_at')
    list_filter = ('resource_type', 'status', 'user')
    search_fields = ('name', 'description', 'location')
    ordering = ('-created_at',)
