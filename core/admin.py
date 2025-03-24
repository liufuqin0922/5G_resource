from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
from .models import User, DeviceArrival, DeviceDelivery, DeviceSecurityStatus, UserActivityLog

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone',)}),
    )

class DeviceArrivalAdmin(ImportExportModelAdmin):
    list_display = ('project_name', 'arrival_date', 'device_model', 'barcode', 'created_by')
    list_filter = ('arrival_date', 'device_model')
    search_fields = ('project_name', 'device_model', 'barcode')
    date_hierarchy = 'arrival_date'
    raw_id_fields = ('created_by',)

class DeviceDeliveryAdmin(ImportExportModelAdmin):
    list_display = ('delivery_date', 'device_model', 'barcode', 'recipient_unit', 'recipient', 'created_by')
    list_filter = ('delivery_date', 'device_model', 'recipient_unit')
    search_fields = ('device_model', 'barcode', 'recipient_unit', 'recipient')
    date_hierarchy = 'delivery_date'
    raw_id_fields = ('created_by',)

class DeviceSecurityStatusAdmin(ImportExportModelAdmin):
    list_display = ('network_element_name', 'is_online', 'asset_serial_number', 'last_check_time', 'created_by')
    list_filter = ('is_online', 'last_check_time')
    search_fields = ('network_element_name', 'asset_serial_number')
    date_hierarchy = 'last_check_time'
    raw_id_fields = ('created_by',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(DeviceArrival, DeviceArrivalAdmin)
admin.site.register(DeviceDelivery, DeviceDeliveryAdmin)
admin.site.register(DeviceSecurityStatus, DeviceSecurityStatusAdmin)

# 用户活动日志
@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'content_type', 'description', 'timestamp', 'ip_address')
    search_fields = ('user__username', 'description', 'ip_address')
    list_filter = ('action_type', 'content_type', 'timestamp')
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'action_type', 'content_type', 'object_id', 'description', 'ip_address', 'user_agent', 'timestamp')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # 只允许超级管理员删除日志
        return request.user.is_superuser
