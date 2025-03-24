from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """自定义用户模型"""
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='手机号')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.username

class DeviceArrival(models.Model):
    """设备到货清单"""
    project_name = models.CharField(max_length=100, verbose_name='项目名称')
    arrival_date = models.DateField(verbose_name='到货日期')
    device_model = models.CharField(max_length=100, verbose_name='设备型号')
    barcode = models.CharField(max_length=100, unique=True, verbose_name='条码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_arrivals', verbose_name='创建人')

    class Meta:
        verbose_name = '设备到货清单'
        verbose_name_plural = verbose_name
        ordering = ['-arrival_date']

    def __str__(self):
        return f"{self.project_name} - {self.device_model} - {self.barcode}"

class DeviceDelivery(models.Model):
    """设备出货清单"""
    delivery_date = models.DateField(verbose_name='领用日期')
    barcode = models.CharField(max_length=100, verbose_name='条码')
    device_model = models.CharField(max_length=100, verbose_name='设备型号')
    recipient_unit = models.CharField(max_length=100, verbose_name='领用单位')
    recipient = models.CharField(max_length=50, verbose_name='领用人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_deliveries', verbose_name='创建人')

    class Meta:
        verbose_name = '设备出货清单'
        verbose_name_plural = verbose_name
        ordering = ['-delivery_date']

    def __str__(self):
        return f"{self.device_model} - {self.barcode} - {self.recipient}"

class DeviceSecurityStatus(models.Model):
    """设备安装状态"""
    network_element_name = models.CharField(max_length=100, verbose_name='网元名称')
    is_online = models.BooleanField(default=True, verbose_name='是否在线')
    asset_serial_number = models.CharField(max_length=100, verbose_name='资产序列号')
    check_date = models.DateField(verbose_name='检查日期', auto_now=False, auto_now_add=False, null=True, blank=True)
    last_check_time = models.DateTimeField(auto_now=True, verbose_name='最后检查时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_security_statuses', verbose_name='创建人')

    class Meta:
        verbose_name = '设备安装状态'
        verbose_name_plural = verbose_name
        ordering = ['-last_check_time']

    def __str__(self):
        return f"{self.network_element_name} - {'在线' if self.is_online else '离线'}"

class UserActivityLog(models.Model):
    """用户操作日志"""
    ACTION_TYPES = (
        ('CREATE', '创建'),
        ('UPDATE', '更新'),
        ('DELETE', '删除'),
        ('VIEW', '查看'),
        ('IMPORT', '导入'),
        ('EXPORT', '导出'),
        ('LOGIN', '登录'),
        ('LOGOUT', '登出'),
        ('OTHER', '其他'),
    )
    
    CONTENT_TYPES = (
        ('DEVICE_ARRIVAL', '设备到货'),
        ('DEVICE_DELIVERY', '设备出货'),
        ('DEVICE_SECURITY', '安装状态'),
        ('USER', '用户'),
        ('SYSTEM', '系统'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs', verbose_name='用户')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name='操作类型')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, verbose_name='内容类型')
    object_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='对象ID')
    description = models.TextField(verbose_name='操作描述')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, null=True, verbose_name='用户代理')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='时间戳')
    
    class Meta:
        verbose_name = '用户操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action_type']),
            models.Index(fields=['content_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.timestamp}"
