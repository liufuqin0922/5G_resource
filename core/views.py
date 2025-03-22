from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from .models import User, Resource5G
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
import pandas as pd
from django.http import HttpResponse
from django.contrib import messages
from .resources import Resource5GResource
from tablib import Dataset

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from .models import User, Resource5G
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms

class RegisterView(CreateView):
    model = User
    template_name = 'core/register.html'
    fields = ['username', 'email', 'phone', 'password']
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'core/logout.html'
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')

# Resource Management Views
class ResourceListView(LoginRequiredMixin, ListView):
    model = Resource5G
    template_name = 'core/resource_list.html'
    context_object_name = 'resources'
    
    def get_queryset(self):
        # Staff can see all resources, regular users only see their own
        if self.request.user.is_staff:
            return Resource5G.objects.all()
        return Resource5G.objects.filter(user=self.request.user)

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource5G
        fields = ['name', 'resource_type', 'description', 'location', 'quantity', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ResourceCreateView(LoginRequiredMixin, CreateView):
    model = Resource5G
    form_class = ResourceForm
    template_name = 'core/resource_form.html'
    success_url = reverse_lazy('resource_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ResourceUpdateView(LoginRequiredMixin, UpdateView):
    model = Resource5G
    form_class = ResourceForm
    template_name = 'core/resource_form.html'
    success_url = reverse_lazy('resource_list')
    
    def get_queryset(self):
        # Staff can update any resource, regular users only their own
        if self.request.user.is_staff:
            return Resource5G.objects.all()
        return Resource5G.objects.filter(user=self.request.user)

class ResourceDeleteView(LoginRequiredMixin, DeleteView):
    model = Resource5G
    template_name = 'core/resource_confirm_delete.html'
    success_url = reverse_lazy('resource_list')
    
    def get_queryset(self):
        # Staff can delete any resource, regular users only their own
        if self.request.user.is_staff:
            return Resource5G.objects.all()
        return Resource5G.objects.filter(user=self.request.user)

class ResourceDetailView(LoginRequiredMixin, DetailView):
    model = Resource5G
    template_name = 'core/resource_detail.html'
    context_object_name = 'resource'
    
    def get_queryset(self):
        # Staff can view any resource, regular users only their own
        if self.request.user.is_staff:
            return Resource5G.objects.all()
        return Resource5G.objects.filter(user=self.request.user)

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

class ResourceExportView(LoginRequiredMixin, View):
    """资源导出视图"""
    
    def get(self, request, *args, **kwargs):
        # 获取要导出的资源
        if request.user.is_staff:
            queryset = Resource5G.objects.all()
        else:
            queryset = Resource5G.objects.filter(user=request.user)
            
        # 创建资源导出器
        resource = Resource5GResource()
        dataset = resource.export(queryset)
        
        # 根据请求的格式返回响应
        fmt = request.GET.get("format", "xlsx")
        
        if fmt == "xlsx":
            response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = "attachment; filename='resources.xlsx'"
            response.content = dataset.export("xlsx")
            return response
        
        # 默认返回Excel格式
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = "attachment; filename='resources.xlsx'"
        response.content = dataset.export("xlsx")
        return response
class ResourceImportView(LoginRequiredMixin, View):
    """资源导入视图"""
    
    def get(self, request, *args, **kwargs):
        return render(request, "core/resource_import.html")
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "只有管理员才能导入资源")
            return redirect("resource_list")
            
        resource = Resource5GResource()
        dataset = Dataset()
        
        if "import_file" in request.FILES:
            import_file = request.FILES["import_file"]
            
            # 检查文件格式
            if import_file.name.endswith(".xlsx"):
                dataset.load(import_file.read(), "xlsx")
            else:
                messages.error(request, "只支持.xlsx格式的文件")
                return redirect("resource_import")
                
            # 导入数据
            result = resource.import_data(dataset, dry_run=True)
            
            if not result.has_errors():
                resource.import_data(dataset, dry_run=False)
                messages.success(request, "资源导入成功")
                return redirect("resource_list")
            else:
                messages.error(request, "导入失败，请检查数据格式")
        
        return redirect("resource_import")