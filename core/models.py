from django.db import models
from django.contrib.auth.models import AbstractUser

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

class Resource5G(models.Model):
    """5G资源模型"""
    RESOURCE_TYPES = (
        ('network', '网络资源'),
        ('spectrum', '频谱资源'),
        ('device', '设备资源'),
    )
    name = models.CharField(max_length=100, verbose_name='资源名称')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, verbose_name='资源类型')
    description = models.TextField(blank=True, null=True, verbose_name='资源描述')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='资源位置')
    quantity = models.IntegerField(default=1, verbose_name='资源数量')
    status = models.BooleanField(default=True, verbose_name='是否可用')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resources', verbose_name='所属用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '5G资源'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name
