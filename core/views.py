from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View, FormView
from django import forms
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from import_export.formats import base_formats
from tablib import Dataset
from django.db import models
from django.utils import timezone

from .models import User, DeviceArrival, DeviceDelivery, DeviceSecurityStatus, UserActivityLog
from .resources import DeviceArrivalResource, DeviceDeliveryResource, DeviceSecurityStatusResource

# Authentication Views
class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='确认密码', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone']
    
    def clean_password_confirm(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password_confirm']:
            raise forms.ValidationError('两次输入的密码不一致')
        return cd['password_confirm']

class RegisterView(TemplateView):
    template_name = 'core/register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RegisterForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})

class LoginView(TemplateView):
    template_name = 'core/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AuthenticationForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})

class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'core/logout.html'
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')
    
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')

# Profile Management Views
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone']

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'core/profile_form.html'
    success_url = reverse_lazy('dashboard')
    
    def get_object(self):
        return self.request.user

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'core/change_password.html', {'form': form})

# Dashboard View
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

# 设备到货清单视图
class DeviceArrivalListView(LoginRequiredMixin, ListView):
    model = DeviceArrival
    template_name = 'core/device_arrival_list.html'
    context_object_name = 'device_arrivals'
    paginate_by = 50  # 设置每页显示50条记录
    
    def get_queryset(self):
        queryset = DeviceArrival.objects.all()  # 所有用户都能看到所有记录
        
        # 搜索功能
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                # 在多个字段中搜索
                models.Q(project_name__icontains=query) |
                models.Q(device_model__icontains=query) |
                models.Q(barcode__icontains=query)
            )
        
        # 按照创建时间倒序排序
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 将搜索关键词加入上下文
        context['query'] = self.request.GET.get('q', '')
        return context

class DeviceArrivalCreateForm(forms.ModelForm):
    class Meta:
        model = DeviceArrival
        fields = ['project_name', 'arrival_date', 'device_model', 'barcode']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance

class DeviceArrivalCreateView(LoginRequiredMixin, CreateView):
    model = DeviceArrival
    form_class = DeviceArrivalCreateForm
    template_name = 'core/device_arrival_form.html'
    success_url = reverse_lazy('device_arrival_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        # 从URL参数中获取条码
        barcode = self.request.GET.get('barcode')
        if barcode:
            # 设置条码初始值
            initial['barcode'] = barcode
            # 尝试查找对应的安装记录
            installation = DeviceSecurityStatus.objects.filter(asset_serial_number=barcode).first()
            if installation:
                # 如果找到对应安装记录，可以提取一些信息
                initial['device_model'] = installation.network_element_name.split('_')[-1] if '_' in installation.network_element_name else '未知型号'
                initial['project_name'] = installation.network_element_name.split('_')[0] if '_' in installation.network_element_name else '未知项目'
                initial['arrival_date'] = timezone.now().date()
        return initial

class DeviceArrivalUpdateView(LoginRequiredMixin, UpdateView):
    model = DeviceArrival
    form_class = DeviceArrivalCreateForm
    template_name = 'core/device_arrival_form.html'
    success_url = reverse_lazy('device_arrival_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return DeviceArrival.objects.all()
        return DeviceArrival.objects.filter(created_by=self.request.user)

class DeviceArrivalDeleteView(LoginRequiredMixin, DeleteView):
    model = DeviceArrival
    template_name = 'core/device_arrival_confirm_delete.html'
    success_url = reverse_lazy('device_arrival_list')
    context_object_name = 'device_arrival'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return DeviceArrival.objects.all()
        return DeviceArrival.objects.filter(created_by=self.request.user)

class DeviceArrivalExportView(LoginRequiredMixin, View):
    """设备到货清单导出视图"""
    
    def get(self, request, *args, **kwargs):
        queryset = DeviceArrival.objects.all()  # 所有用户都能导出所有记录
            
        resource = DeviceArrivalResource()
        dataset = resource.export(queryset)
        
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="device_arrivals.xlsx"'
        response.content = dataset.export("xlsx")
        return response

class DeviceArrivalImportView(LoginRequiredMixin, TemplateView):
    """设备到货导入视图"""
    template_name = 'core/device_arrival_import.html'
    
    def post(self, request, *args, **kwargs):
        resource = DeviceArrivalResource()
        dataset = Dataset()
        
        # 获取上传的文件
        import_file = request.FILES.get('import_file')
        if not import_file:
            messages.error(request, "请选择上传文件")
            return HttpResponseRedirect(reverse_lazy('device_arrival_import'))
        
        try:
            # 检查文件类型
            if not import_file.name.endswith(('.xls', '.xlsx')):
                messages.error(request, "只接受Excel文件(.xls, .xlsx)")
                return HttpResponseRedirect(reverse_lazy('device_arrival_import'))
            
            # 尝试加载Excel内容
            try:
                imported_data = dataset.load(import_file.read(), format='xlsx')
            except Exception as e:
                messages.error(request, f"Excel文件读取失败: {str(e)}")
                return HttpResponseRedirect(reverse_lazy('device_arrival_import'))
            
            # 关联创建者
            def before_import(dataset, dry_run, **kwargs):
                for row in dataset.dict:
                    row['created_by'] = request.user.id
            
            # 设置导入前回调
            result = resource.import_data(dataset, dry_run=True, before_import=before_import)
            
            # 检查导入结果
            if result.has_errors():
                # 汇总错误信息
                error_rows = []
                for error in result.row_errors():
                    row_number = error[0]
                    error_info = "、".join([f"{field}: {err.error}" for field, errors in error[1].items() for err in errors])
                    error_rows.append(f"行 {row_number}: {error_info}")
                
                error_message = "、".join(error_rows[:10])
                if len(error_rows) > 10:
                    error_message += f"...等{len(error_rows)}个错误"
                
                messages.error(request, f"导入数据有错误: {error_message}")
                return HttpResponseRedirect(reverse_lazy('device_arrival_import'))
            
            # 正式导入数据
            result = resource.import_data(dataset, dry_run=False, before_import=before_import)
            
            # 导入成功
            messages.success(request, f"成功导入{result.total_rows}行数据")
            
        except Exception as e:
            messages.error(request, f"导入过程发生错误: {str(e)}")
        
        return HttpResponseRedirect(reverse_lazy('device_arrival_list'))

# 设备出货清单视图
class DeviceDeliveryListView(LoginRequiredMixin, ListView):
    model = DeviceDelivery
    template_name = 'core/device_delivery_list.html'
    context_object_name = 'device_deliveries'
    paginate_by = 50  # 设置每页显示50条记录
    
    def get_queryset(self):
        queryset = DeviceDelivery.objects.all()  # 所有用户都能看到所有记录
        
        # 搜索功能
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                # 在多个字段中搜索
                models.Q(device_model__icontains=query) |
                models.Q(barcode__icontains=query) |
                models.Q(recipient_unit__icontains=query) |
                models.Q(recipient__icontains=query)
            )
        
        # 按照创建时间倒序排序
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 将搜索关键词加入上下文
        context['query'] = self.request.GET.get('q', '')
        return context

class DeviceDeliveryCreateForm(forms.ModelForm):
    class Meta:
        model = DeviceDelivery
        fields = ['delivery_date', 'barcode', 'device_model', 'recipient_unit', 'recipient']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance

class DeviceDeliveryCreateView(LoginRequiredMixin, CreateView):
    model = DeviceDelivery
    form_class = DeviceDeliveryCreateForm
    template_name = 'core/device_delivery_form.html'
    success_url = reverse_lazy('device_delivery_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class DeviceDeliveryUpdateView(LoginRequiredMixin, UpdateView):
    model = DeviceDelivery
    form_class = DeviceDeliveryCreateForm
    template_name = 'core/device_delivery_form.html'
    success_url = reverse_lazy('device_delivery_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return DeviceDelivery.objects.all()
        return DeviceDelivery.objects.filter(created_by=self.request.user)

class DeviceDeliveryDeleteView(LoginRequiredMixin, DeleteView):
    model = DeviceDelivery
    template_name = 'core/device_delivery_confirm_delete.html'
    success_url = reverse_lazy('device_delivery_list')
    context_object_name = 'device_delivery'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return DeviceDelivery.objects.all()
        return DeviceDelivery.objects.filter(created_by=self.request.user)

class DeviceDeliveryExportView(LoginRequiredMixin, View):
    """设备出货清单导出视图"""
    
    def get(self, request, *args, **kwargs):
        queryset = DeviceDelivery.objects.all()  # 所有用户都能导出所有记录
            
        resource = DeviceDeliveryResource()
        dataset = resource.export(queryset)
        
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="device_deliveries.xlsx"'
        response.content = dataset.export("xlsx")
        return response

class DeviceDeliveryImportView(LoginRequiredMixin, TemplateView):
    """设备出货清单导入视图"""
    template_name = 'core/device_delivery_import.html'
    
    def post(self, request, *args, **kwargs):
        resource = DeviceDeliveryResource()
        dataset = Dataset()
        
        # 获取上传的文件
        import_file = request.FILES.get('import_file')
        if not import_file:
            messages.error(request, "请选择上传文件")
            return HttpResponseRedirect(reverse_lazy('device_delivery_import'))
        
        try:
            # 检查文件类型
            if not import_file.name.endswith(('.xls', '.xlsx')):
                messages.error(request, "只接受Excel文件(.xls, .xlsx)")
                return HttpResponseRedirect(reverse_lazy('device_delivery_import'))
            
            # 尝试加载Excel内容
            try:
                imported_data = dataset.load(import_file.read(), format='xlsx')
            except Exception as e:
                messages.error(request, f"Excel文件读取失败: {str(e)}")
                return HttpResponseRedirect(reverse_lazy('device_delivery_import'))
            
            # 关联创建者
            def before_import(dataset, dry_run, **kwargs):
                for row in dataset.dict:
                    row['created_by'] = request.user.id
            
            # 设置导入前回调
            result = resource.import_data(dataset, dry_run=True, before_import=before_import)
            
            # 检查导入结果
            if result.has_errors():
                # 汇总错误信息
                error_rows = []
                for error in result.row_errors():
                    row_number = error[0]
                    error_info = "、".join([f"{field}: {err.error}" for field, errors in error[1].items() for err in errors])
                    error_rows.append(f"行 {row_number}: {error_info}")
                
                error_message = "、".join(error_rows[:10])
                if len(error_rows) > 10:
                    error_message += f"...等{len(error_rows)}个错误"
                
                messages.error(request, f"导入数据有错误: {error_message}")
                return HttpResponseRedirect(reverse_lazy('device_delivery_import'))
            
            # 正式导入数据
            result = resource.import_data(dataset, dry_run=False, before_import=before_import)
            
            # 导入成功
            messages.success(request, f"成功导入{result.total_rows}行数据")
            
        except Exception as e:
            messages.error(request, f"导入过程发生错误: {str(e)}")
        
        return HttpResponseRedirect(reverse_lazy('device_delivery_list'))

# 设备安全状态视图
class DeviceSecurityStatusListView(LoginRequiredMixin, ListView):
    model = DeviceSecurityStatus
    template_name = 'core/device_security_status_list.html'
    context_object_name = 'device_statuses'
    paginate_by = 50  # 设置每页显示50条记录
    
    def get_queryset(self):
        queryset = DeviceSecurityStatus.objects.all()  # 所有用户都能看到所有记录
        
        # 搜索功能
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                # 在多个字段中搜索
                models.Q(network_element_name__icontains=query) |
                models.Q(asset_serial_number__icontains=query)
            )
        
        # 增加在线状态筛选
        online_status = self.request.GET.get('status')
        if online_status == 'online':
            queryset = queryset.filter(is_online=True)
        elif online_status == 'offline':
            queryset = queryset.filter(is_online=False)
        
        # 按照最后检查时间倒序排序
        return queryset.order_by('-last_check_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 将搜索关键词和状态筛选加入上下文
        context['query'] = self.request.GET.get('q', '')
        context['status'] = self.request.GET.get('status', '')
        return context

class DeviceSecurityStatusCreateForm(forms.ModelForm):
    class Meta:
        model = DeviceSecurityStatus
        fields = ['network_element_name', 'is_online', 'asset_serial_number', 'check_date']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance

class DeviceSecurityStatusCreateView(LoginRequiredMixin, CreateView):
    model = DeviceSecurityStatus
    form_class = DeviceSecurityStatusCreateForm
    template_name = 'core/device_security_status_form.html'
    success_url = reverse_lazy('device_security_status_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        # 从URL参数中获取条码
        barcode = self.request.GET.get('barcode')
        if barcode:
            # 设置资产序列号初始值为条码
            initial['asset_serial_number'] = barcode
            initial['is_online'] = True  # 默认设置为在线
            # 尝试查找对应的到货记录
            arrival = DeviceArrival.objects.filter(barcode=barcode).first()
            if arrival:
                initial['network_element_name'] = f"{arrival.project_name}_{arrival.device_model}"
                initial['check_date'] = timezone.now().date()
        return initial

class DeviceSecurityStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = DeviceSecurityStatus
    form_class = DeviceSecurityStatusCreateForm
    template_name = 'core/device_security_status_form.html'
    success_url = reverse_lazy('device_security_status_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return DeviceSecurityStatus.objects.all()
        return DeviceSecurityStatus.objects.filter(created_by=self.request.user)

class DeviceSecurityStatusDeleteView(LoginRequiredMixin, DeleteView):
    model = DeviceSecurityStatus
    template_name = 'core/device_security_status_confirm_delete.html'
    success_url = reverse_lazy('device_security_status_list')
    context_object_name = 'device_security_status'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return DeviceSecurityStatus.objects.all()
        return DeviceSecurityStatus.objects.filter(created_by=self.request.user)

class DeviceSecurityStatusExportView(LoginRequiredMixin, View):
    """设备安全状态导出视图"""
    
    def get(self, request, *args, **kwargs):
        queryset = DeviceSecurityStatus.objects.all()  # 所有用户都能导出所有记录
            
        resource = DeviceSecurityStatusResource()
        dataset = resource.export(queryset)
        
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="device_security_statuses.xlsx"'
        response.content = dataset.export("xlsx")
        return response

class DeviceSecurityStatusImportView(LoginRequiredMixin, TemplateView):
    """设备安装状态导入视图"""
    template_name = 'core/device_security_status_import.html'
    
    def post(self, request, *args, **kwargs):
        resource = DeviceSecurityStatusResource()
        dataset = Dataset()
        
        # 获取上传的文件
        import_file = request.FILES.get('import_file')
        if not import_file:
            messages.error(request, "请选择上传文件")
            return HttpResponseRedirect(reverse_lazy('device_security_status_import'))
        
        try:
            # 检查文件类型
            if not import_file.name.endswith(('.xls', '.xlsx')):
                messages.error(request, "只接受Excel文件(.xls, .xlsx)")
                return HttpResponseRedirect(reverse_lazy('device_security_status_import'))
            
            # 尝试加载Excel内容
            try:
                imported_data = dataset.load(import_file.read(), format='xlsx')
            except Exception as e:
                messages.error(request, f"Excel文件读取失败: {str(e)}")
                return HttpResponseRedirect(reverse_lazy('device_security_status_import'))
            
            # 关联创建者
            def before_import(dataset, dry_run, **kwargs):
                for row in dataset.dict:
                    row['created_by'] = request.user.id
            
            # 设置导入前回调
            result = resource.import_data(dataset, dry_run=True, before_import=before_import)
            
            # 检查导入结果
            if result.has_errors():
                # 汇总错误信息
                error_rows = []
                for error in result.row_errors():
                    row_number = error[0]
                    error_info = "、".join([f"{field}: {err.error}" for field, errors in error[1].items() for err in errors])
                    error_rows.append(f"行 {row_number}: {error_info}")
                
                error_message = "、".join(error_rows[:10])
                if len(error_rows) > 10:
                    error_message += f"...等{len(error_rows)}个错误"
                
                messages.error(request, f"导入数据有错误: {error_message}")
                return HttpResponseRedirect(reverse_lazy('device_security_status_import'))
            
            # 正式导入数据
            result = resource.import_data(dataset, dry_run=False, before_import=before_import)
            
            # 导入成功
            messages.success(request, f"成功导入{result.total_rows}行数据")
            
        except Exception as e:
            messages.error(request, f"导入过程发生错误: {str(e)}")
        
        return HttpResponseRedirect(reverse_lazy('device_security_status_list'))

class DashboardStatusView(LoginRequiredMixin, TemplateView):
    """设备状态看板视图"""
    template_name = 'core/dashboard_status.html'
    items_per_page = 20  # 每页显示的设备数量
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取当前页码
        page = self.request.GET.get('page', 1)
        device_type = self.request.GET.get('type', 'online')  # 默认显示在线设备
        try:
            page = int(page)
        except ValueError:
            page = 1
        
        # 限制查询的时间范围，只获取最近24小时的数据
        date_limit = timezone.now() - timezone.timedelta(hours=24)
        
        # 只获取必要的字段，减少内存使用
        arrivals = DeviceArrival.objects.filter(
            created_at__gte=date_limit
        ).values('barcode', 'device_model', 'project_name', 'arrival_date')
        
        installations = DeviceSecurityStatus.objects.filter(
            created_at__gte=date_limit
        ).values('asset_serial_number', 'network_element_name', 'is_online', 'check_date')
        
        # 使用字典代替多次查询，提高效率
        arrival_dict = {item['barcode']: item for item in arrivals if item['barcode']}
        installation_dict = {item['asset_serial_number']: item for item in installations if item['asset_serial_number']}
        
        # 高效计算设备分类
        arrival_barcodes = set(arrival_dict.keys())
        installation_serials = set(installation_dict.keys())
        
        # 计算不同情况的设备
        online_devices = arrival_barcodes.intersection(installation_serials)
        offline_devices = arrival_barcodes.difference(installation_serials)
        other_devices = installation_serials.difference(arrival_barcodes)
        
        # 获取今日数据
        today = timezone.now().date()
        
        today_installations = DeviceSecurityStatus.objects.filter(
            created_at__date=today
        ).values('is_online')
        
        today_online_count = sum(1 for item in today_installations if item['is_online'])
        today_offline_count = len(today_installations) - today_online_count
        
        # 准备分页数据
        if device_type == 'online':
            all_devices = list(online_devices)
            device_label = '在线设备'
        elif device_type == 'offline':
            all_devices = list(offline_devices)
            device_label = '脱网设备'
        else:  # 'other'
            all_devices = list(other_devices)
            device_label = '其他设备'
            
        # 计算总页数
        total_devices = len(all_devices)
        total_pages = (total_devices + self.items_per_page - 1) // self.items_per_page
        
        # 确保页码有效
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages
            
        # 计算当前页的设备
        start_idx = (page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        current_page_devices = all_devices[start_idx:end_idx]
        
        # 生成当前设备列表
        device_list = []
        
        if device_type == 'online':
            for barcode in current_page_devices:
                arrival = arrival_dict.get(barcode)
                installation = installation_dict.get(barcode)
                if arrival and installation:
                    device_list.append({
                        'barcode': barcode,
                        'device_model': arrival['device_model'],
                        'project_name': arrival['project_name'],
                        'network_element_name': installation['network_element_name'],
                        'is_online': installation['is_online'],
                        'check_date': installation['check_date'],
                    })
        elif device_type == 'offline':
            for barcode in current_page_devices:
                arrival = arrival_dict.get(barcode)
                if arrival:
                    device_list.append({
                        'barcode': barcode,
                        'device_model': arrival['device_model'],
                        'project_name': arrival['project_name'],
                        'arrival_date': arrival['arrival_date'],
                    })
        else:  # 'other'
            for serial in current_page_devices:
                installation = installation_dict.get(serial)
                if installation:
                    device_list.append({
                        'serial': serial,
                        'network_element_name': installation['network_element_name'],
                        'is_online': installation['is_online'],
                        'check_date': installation['check_date'],
                    })
        
        # 为了向后兼容，保留原来的列表
        online_device_list = []
        offline_device_list = []
        other_device_list = []
        
        # 限制数量以减少内存使用
        if device_type == 'online':
            online_device_list = device_list
        elif device_type == 'offline':
            offline_device_list = device_list
        else:
            other_device_list = device_list
        
        # 添加数据到上下文
        context.update({
            'online_count': len(online_devices),
            'offline_count': len(offline_devices),
            'other_count': len(other_devices),
            'today_online_count': today_online_count,
            'today_offline_count': today_offline_count,
            'online_device_list': online_device_list,
            'offline_device_list': offline_device_list,
            'other_device_list': other_device_list,
            'today': today,
            'is_limited_view': True,
            'date_range': f"过去24小时 ({date_limit.strftime('%Y-%m-%d %H:%M')} 至今)",
            
            # 分页信息
            'current_page': page,
            'total_pages': total_pages,
            'total_devices': total_devices,
            'device_type': device_type,
            'device_label': device_label,
            'device_list': device_list,
            'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        })
        
        return context

class UserActivityLogListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """用户操作日志列表视图，仅管理员可访问"""
    model = UserActivityLog
    template_name = 'core/user_activity_log_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    ordering = ['-timestamp']
    
    def test_func(self):
        """检查用户是否是管理员"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_queryset(self):
        """根据筛选条件获取查询集"""
        queryset = super().get_queryset()
        
        # 获取筛选参数
        user_id = self.request.GET.get('user')
        action_type = self.request.GET.get('action_type')
        content_type = self.request.GET.get('content_type')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        search = self.request.GET.get('search')
        
        # 应用筛选
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
        if search:
            queryset = queryset.filter(
                models.Q(description__icontains=search) |
                models.Q(user__username__icontains=search) |
                models.Q(ip_address__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """添加额外上下文数据"""
        context = super().get_context_data(**kwargs)
        
        # 添加筛选选项
        context['users'] = User.objects.all()
        context['action_types'] = UserActivityLog.ACTION_TYPES
        context['content_types'] = UserActivityLog.CONTENT_TYPES
        
        # 保持筛选条件
        context['selected_user'] = self.request.GET.get('user', '')
        context['selected_action_type'] = self.request.GET.get('action_type', '')
        context['selected_content_type'] = self.request.GET.get('content_type', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['search'] = self.request.GET.get('search', '')
        
        return context