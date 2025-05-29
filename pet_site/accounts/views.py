from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .forms import LoginForm, RegisterForm, UserProfileForm, PasswordChangeCustomForm


def home_view(request):
    return render(request, 'accounts/home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, '登录成功！')
                return redirect('home')
            else:
                messages.error(request, '用户名或密码错误')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('home')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, '您已成功退出登录')
    return redirect('home')


@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')


@login_required
def user_settings_view(request):
    """用户设置主页面"""
    return render(request, 'accounts/user_settings.html')


@login_required
def profile_settings_view(request):
    """用户基本信息设置"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息更新成功！')
            return redirect('accounts:profile_settings')
        else:
            messages.error(request, '请检查输入的信息是否正确')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile_settings.html', {'form': form})


@login_required
def security_settings_view(request):
    """安全设置"""
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # 保持登录状态
            messages.success(request, '密码修改成功！')
            return redirect('accounts:security_settings')
        else:
            messages.error(request, '请检查输入的信息')
    else:
        form = PasswordChangeCustomForm(request.user)
    
    return render(request, 'accounts/security_settings.html', {'form': form})


@login_required
@require_http_methods(["POST"])
def delete_profile_picture(request):
    """删除用户头像"""
    if request.user.profile_picture:
        request.user.profile_picture.delete()
        request.user.save()
        return JsonResponse({'success': True, 'message': '头像删除成功'})
    return JsonResponse({'success': False, 'message': '没有头像可删除'})


@login_required
def account_info_view(request):
    """账户信息查看"""
    context = {
        'user': request.user,
        'account_created': request.user.date_joined,
        'last_login': request.user.last_login,
        'settings_updated': request.user.settings_updated_at,
    }
    return render(request, 'accounts/account_info.html', context)