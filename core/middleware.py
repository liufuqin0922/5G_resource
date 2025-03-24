import re
import json
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import UserActivityLog
from django.dispatch import receiver

class UserActivityLogMiddleware(MiddlewareMixin):
    """记录用户活动的中间件"""
    
    IGNORE_PATHS = [
        r'^/static/',
        r'^/media/',
        r'^/admin/jsi18n/',
        r'^/__debug__/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.path_to_content_type = {
            r'^/device-arrival/': 'DEVICE_ARRIVAL',
            r'^/device-delivery/': 'DEVICE_DELIVERY',
            r'^/device-security-status/': 'DEVICE_SECURITY',
            r'^/users/': 'USER',
            r'^/login/': 'USER',
            r'^/logout/': 'USER',
            r'^/register/': 'USER',
            r'^/profile/': 'USER',
            r'^/dashboard/': 'SYSTEM',
        }
        
        self.method_to_action = {
            'GET': lambda path: 'VIEW' if not any(p in path for p in ['/export', '/download']) else 'EXPORT',
            'POST': lambda path: 'CREATE' if not '/import/' in path else 'IMPORT',
            'PUT': lambda path: 'UPDATE',
            'PATCH': lambda path: 'UPDATE',
            'DELETE': lambda path: 'DELETE',
        }
        
    def should_log(self, path):
        """检查是否应该记录此路径"""
        return not any(re.match(pattern, path) for pattern in self.IGNORE_PATHS)
    
    def get_content_type(self, path):
        """根据路径确定内容类型"""
        for pattern, content_type in self.path_to_content_type.items():
            if re.match(pattern, path):
                return content_type
        return 'SYSTEM'
    
    def get_action_type(self, request):
        """根据请求方法确定操作类型"""
        method = request.method
        path = request.path
        
        if method in self.method_to_action:
            return self.method_to_action[method](path)
        return 'OTHER'
    
    def get_object_id(self, request, resolved_path):
        """尝试获取操作对象的ID"""
        if resolved_path.url_name and any(x in resolved_path.url_name for x in ['detail', 'update', 'delete']):
            if resolved_path.kwargs.get('pk'):
                return resolved_path.kwargs.get('pk')
        return None
    
    def get_description(self, request, action_type, content_type, object_id):
        """生成操作描述"""
        url_name = resolve(request.path).url_name or ''
        if action_type == 'LOGIN':
            return '用户登录'
        elif action_type == 'LOGOUT':
            return '用户登出'
        
        action_desc = {
            'CREATE': '创建了',
            'UPDATE': '更新了',
            'DELETE': '删除了',
            'VIEW': '查看了',
            'IMPORT': '导入了',
            'EXPORT': '导出了',
            'OTHER': '操作了'
        }.get(action_type, '操作了')
        
        content_desc = {
            'DEVICE_ARRIVAL': '设备到货记录',
            'DEVICE_DELIVERY': '设备出货记录',
            'DEVICE_SECURITY': '设备安装状态',
            'USER': '用户信息',
            'SYSTEM': '系统'
        }.get(content_type, '未知内容')
        
        if object_id:
            return f"{action_desc}{content_desc} ID:{object_id}"
        
        return f"{action_desc}{content_desc}"
    
    def process_request(self, request):
        """处理请求"""
        request.log_data = {}
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """处理视图函数"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.log_data['view_func'] = view_func.__name__
            request.log_data['view_args'] = view_args
            request.log_data['view_kwargs'] = view_kwargs
    
    def process_response(self, request, response):
        """处理响应并记录活动日志"""
        if (hasattr(request, 'user') and request.user.is_authenticated and
                self.should_log(request.path)):
            
            path = request.path
            resolved_path = resolve(path)
            
            # 获取操作信息
            action_type = self.get_action_type(request)
            content_type = self.get_content_type(path)
            object_id = self.get_object_id(request, resolved_path)
            description = self.get_description(request, action_type, content_type, object_id)
            
            # 获取IP和用户代理
            ip_address = request.META.get('REMOTE_ADDR', '')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # 创建日志记录
            try:
                UserActivityLog.objects.create(
                    user=request.user,
                    action_type=action_type,
                    content_type=content_type,
                    object_id=object_id,
                    description=description,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            except Exception as e:
                # 记录失败不应影响正常响应
                print(f"Failed to log user activity: {e}")
        
        return response

# 添加信号处理器来记录登录和登出事件
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """记录用户登录"""
    try:
        UserActivityLog.objects.create(
            user=user,
            action_type='LOGIN',
            content_type='USER',
            description='用户登录',
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    except Exception as e:
        print(f"Failed to log user login: {e}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """记录用户登出"""
    if user:
        try:
            UserActivityLog.objects.create(
                user=user,
                action_type='LOGOUT',
                content_type='USER',
                description='用户登出',
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception as e:
            print(f"Failed to log user logout: {e}") 