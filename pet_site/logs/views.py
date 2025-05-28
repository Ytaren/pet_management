from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, Http404
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json
import requests
from collections import Counter

from .models import PetLog
from .forms import PetLogForm, PetLogFilterForm, AIAnalysisForm
from pets.models import Pet
from .ai_service import pet_log_analyzer


# =============================================================================
# 新增：统一日志中心和智能功能
# =============================================================================

@login_required
def logs_center_view(request):
    """统一的日志中心页面 - 新的主入口"""
    user_pets = Pet.objects.filter(owner=request.user)
    
    # 获取智能提醒
    reminders = get_intelligent_reminders(request.user)
    
    # 最近活动
    recent_activities = PetLog.objects.filter(
        pet__owner=request.user
    ).select_related('pet').order_by('-created_at')[:8]
    
    # 快速统计
    total_logs = PetLog.objects.filter(pet__owner=request.user).count()
    quick_stats = {
        'total_pets': user_pets.count(),
        'total_logs': total_logs,
        'pets_need_attention': len([r for r in reminders if r['priority'] in ['high', 'medium']]),
        'recent_logs_count': recent_activities.count(),
    }
    
    # 每只宠物的状态概览
    pets_overview = []
    for pet in user_pets:
        last_log = PetLog.objects.filter(pet=pet).order_by('-date').first()
        log_count = PetLog.objects.filter(pet=pet).count()
        
        days_since_last = None
        if last_log:
            days_since_last = (timezone.now().date() - last_log.date).days
        
        pets_overview.append({
            'pet': pet,
            'last_log': last_log,
            'log_count': log_count,
            'days_since_last': days_since_last,
            'needs_attention': days_since_last is None or days_since_last >= 3,
        })
    
    context = {
        'reminders': reminders,
        'recent_activities': recent_activities,
        'quick_stats': quick_stats,
        'pets_overview': pets_overview,
        'user_pets': user_pets,
    }
    
    return render(request, 'logs/logs_center.html', context)


@require_POST
@login_required
def quick_log_create(request):
    """快速创建日志的API"""
    try:
        data = json.loads(request.body)
        pet_id = data.get('pet_id')
        
        if not pet_id:
            return JsonResponse({'success': False, 'error': '请选择宠物'}, status=400)
        
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        
        # 创建日志记录
        log = PetLog.objects.create(
            pet=pet,
            date=data.get('date', timezone.now().date()),
            mood=data.get('mood', 'normal'),
            activity_level=data.get('activity_level', 'normal'),
            food_intake=data.get('food_intake') or None,
            water_intake=data.get('water_intake') or None,
            weight=data.get('weight') or None,
            length=data.get('length') or None,
            notes=data.get('notes', '')
        )
        
        # 智能建议下一步操作
        suggestions = []
        pet_logs_count = PetLog.objects.filter(pet=pet).count()
        
        if log.weight and pet_logs_count >= 5:
            suggestions.append({
                'action': 'ai_analysis',
                'text': '数据足够，建议进行AI健康分析',
                'url': reverse('logs:ai_analysis_for_pet', args=[pet.id]),
                'icon': 'fas fa-brain'
            })
        
        if pet_logs_count >= 3:
            suggestions.append({
                'action': 'view_trends',
                'text': '查看趋势图表',
                'url': reverse('logs:pet_logs', args=[pet.id]),
                'icon': 'fas fa-chart-line'
            })
        
        return JsonResponse({
            'success': True,
            'log_id': log.id,
            'suggestions': suggestions,
            'message': f'成功记录 {pet.name} 的日志',
            'redirect_url': reverse('logs:logs_center')
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'保存失败: {str(e)}'
        }, status=400)


@login_required
def get_smart_reminders(request):
    """获取智能提醒的API"""
    reminders = get_intelligent_reminders(request.user)
    return JsonResponse({
        'success': True,
        'reminders': reminders
    })


def get_intelligent_reminders(user):
    """获取智能提醒"""
    reminders = []
    user_pets = Pet.objects.filter(owner=user)
    
    for pet in user_pets:
        last_log = PetLog.objects.filter(pet=pet).order_by('-date').first()
        
        if not last_log:
            reminders.append({
                'type': 'first_log',
                'pet_id': pet.id,
                'pet_name': pet.name,
                'message': f'还没有为 {pet.name} 创建过日志记录',
                'priority': 'high',
                'action_text': '立即记录',
                'action_url': reverse('logs:log_create_for_pet', args=[pet.id]),
                'icon': 'fas fa-plus-circle'
            })
        else:
            days_since_last = (timezone.now().date() - last_log.date).days
            
            if days_since_last >= 7:
                reminders.append({
                    'type': 'long_gap',
                    'pet_id': pet.id,
                    'pet_name': pet.name,
                    'message': f'{pet.name} 已经 {days_since_last} 天没有记录了',
                    'priority': 'medium',
                    'action_text': '补充记录',
                    'action_url': reverse('logs:log_create_for_pet', args=[pet.id]),
                    'icon': 'fas fa-exclamation-triangle'
                })
            elif days_since_last >= 3:
                reminders.append({
                    'type': 'regular_reminder',
                    'pet_id': pet.id,
                    'pet_name': pet.name,
                    'message': f'建议记录 {pet.name} 的最新状态',
                    'priority': 'low',
                    'action_text': '记录状态',
                    'action_url': reverse('logs:log_create_for_pet', args=[pet.id]),
                    'icon': 'fas fa-clock'
                })
    
    # 按优先级排序
    priority_order = {'high': 3, 'medium': 2, 'low': 1}
    return sorted(reminders, key=lambda x: priority_order[x['priority']], reverse=True)


# =============================================================================
# 原有视图类保持不变
# =============================================================================

class PetLogListView(LoginRequiredMixin, ListView):
    """宠物日志列表视图"""
    model = PetLog
    template_name = 'logs/log_list.html'
    context_object_name = 'logs'
    paginate_by = 20
    
    def get_queryset(self):
        """获取当前用户的宠物日志"""
        queryset = PetLog.objects.filter(pet__owner=self.request.user).select_related('pet')
        
        # 应用过滤器
        form = PetLogFilterForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            if form.cleaned_data.get('pet'):
                queryset = queryset.filter(pet=form.cleaned_data['pet'])
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(date__lte=form.cleaned_data['date_to'])
            if form.cleaned_data.get('mood'):
                queryset = queryset.filter(mood=form.cleaned_data['mood'])
            if form.cleaned_data.get('activity_level'):
                queryset = queryset.filter(activity_level=form.cleaned_data['activity_level'])
        
        return queryset.order_by('-date', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = PetLogFilterForm(self.request.GET, user=self.request.user)
        context['user_pets'] = Pet.objects.filter(owner=self.request.user)
        
        # 统计信息
        user_logs = PetLog.objects.filter(pet__owner=self.request.user)
        context['stats'] = {
            'total_logs': user_logs.count(),
            'pets_with_logs': user_logs.values('pet').distinct().count(),
            'recent_logs': user_logs.filter(date__gte=timezone.now().date() - timedelta(days=7)).count(),
        }
        
        return context


class PetLogDetailView(LoginRequiredMixin, DetailView):
    """宠物日志详情视图"""
    model = PetLog
    template_name = 'logs/log_detail.html'
    context_object_name = 'log'
    
    def get_queryset(self):
        return PetLog.objects.filter(pet__owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取相邻的日志记录
        log = self.get_object()
        context['previous_log'] = PetLog.objects.filter(
            pet=log.pet,
            date__lt=log.date
        ).order_by('-date').first()
        
        context['next_log'] = PetLog.objects.filter(
            pet=log.pet,
            date__gt=log.date
        ).order_by('date').first()
        
        return context


class PetLogCreateView(LoginRequiredMixin, CreateView):
    """创建宠物日志视图"""
    model = PetLog
    form_class = PetLogForm
    template_name = 'logs/log_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        
        # 如果URL中指定了宠物ID
        pet_id = self.kwargs.get('pet_id')
        if pet_id:
            try:
                pet = Pet.objects.get(id=pet_id, owner=self.request.user)
                kwargs['initial_pet'] = pet
            except Pet.DoesNotExist:
                raise Http404("宠物不存在")
        
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f"成功为 {form.instance.pet.name} 添加了日志记录")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('logs:log_detail', kwargs={'pk': self.object.pk})


class PetLogUpdateView(LoginRequiredMixin, UpdateView):
    """更新宠物日志视图"""
    model = PetLog
    form_class = PetLogForm
    template_name = 'logs/log_form.html'
    
    def get_queryset(self):
        return PetLog.objects.filter(pet__owner=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f"成功更新了 {form.instance.pet.name} 的日志记录")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('logs:log_detail', kwargs={'pk': self.object.pk})


class PetLogDeleteView(LoginRequiredMixin, DeleteView):
    """删除宠物日志视图"""
    model = PetLog
    template_name = 'logs/log_confirm_delete.html'
    success_url = reverse_lazy('logs:log_list')
    
    def get_queryset(self):
        return PetLog.objects.filter(pet__owner=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        log = self.get_object()
        messages.success(request, f"成功删除了 {log.pet.name} 在 {log.date} 的日志记录")
        return super().delete(request, *args, **kwargs)


@login_required
def pet_logs_by_pet(request, pet_id):
    """特定宠物的日志列表"""
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    logs = PetLog.objects.filter(pet=pet).order_by('-date')
      # 统计信息
    latest_log_with_weight = logs.exclude(weight__isnull=True).first()
    stats = {
        'total_logs': logs.count(),
        'date_range': {
            'first': logs.last().date if logs.exists() else None,
            'last': logs.first().date if logs.exists() else None,
        },
        'latest_weight': latest_log_with_weight.weight if latest_log_with_weight else None,
        'recent_logs': logs.filter(date__gte=timezone.now().date() - timedelta(days=30)).count(),
    }
    
    context = {
        'pet': pet,
        'logs': logs,
        'stats': stats,
    }
    
    return render(request, 'logs/pet_logs.html', context)


@login_required
def dashboard_view(request):
    """日志仪表板"""
    user_pets = Pet.objects.filter(owner=request.user)
    
    # 最近的日志
    recent_logs = PetLog.objects.filter(
        pet__owner=request.user
    ).select_related('pet').order_by('-date')[:10]
    
    # 统计信息
    stats = {}
    for pet in user_pets:
        pet_logs = PetLog.objects.filter(pet=pet)
        stats[pet.id] = {
            'name': pet.name,
            'total_logs': pet_logs.count(),
            'latest_log': pet_logs.order_by('-date').first(),
            'avg_weight': pet_logs.exclude(weight__isnull=True).aggregate(Avg('weight'))['weight__avg'],
            'days_since_last_log': None,
        }
        
        if stats[pet.id]['latest_log']:
            days_diff = (timezone.now().date() - stats[pet.id]['latest_log'].date).days
            stats[pet.id]['days_since_last_log'] = days_diff
    
    context = {
        'user_pets': user_pets,
        'recent_logs': recent_logs,
        'stats': stats,
    }
    
    return render(request, 'logs/dashboard.html', context)


@login_required
def ai_analysis_view(request, pet_id=None):
    """AI分析视图 - 增强版，支持预选宠物"""
    # 如果URL中指定了宠物ID，预选该宠物
    initial_pet = None
    if pet_id:
        try:
            initial_pet = Pet.objects.get(id=pet_id, owner=request.user)
        except Pet.DoesNotExist:
            messages.error(request, "指定的宠物不存在")
            return redirect('logs:ai_analysis')
    
    if request.method == 'POST':
        form = AIAnalysisForm(request.POST, user=request.user)
        if form.is_valid():
            pet = form.cleaned_data['pet']
            period = int(form.cleaned_data['analysis_period'])
            analysis_types = form.cleaned_data['analysis_type']
            
            # 获取分析数据
            raw_analysis_data = PetLog.objects.get_analysis_data(pet, period)
            
            if raw_analysis_data['logs_summary']['total_logs'] == 0:
                messages.warning(request, f"{pet.name} 在最近 {period} 天内没有日志记录")
                return redirect('logs:ai_analysis')
            
            # 转换数据格式为AI服务期望的格式
            analysis_data = convert_analysis_data_format(raw_analysis_data)
            
            # 调用AI分析服务
            try:
                print(f"🔍 开始AI分析 - 宠物: {pet.name}, 分析类型: {analysis_types}")
                print(f"📊 转换后数据统计:")
                print(f"  - 平均体重: {analysis_data['logs_summary']['avg_weight']:.2f}kg")
                print(f"  - 平均身长: {analysis_data['logs_summary']['avg_length']:.2f}cm")
                print(f"  - 最近记录数: {len(analysis_data['recent_logs'])}")
                ai_result = call_ai_analysis_service(analysis_data, analysis_types)
                print(f"✅ AI分析完成 - 结果类型: {type(ai_result)}")
                
                context = {
                    'pet': pet,
                    'analysis_data': analysis_data,
                    'ai_result': ai_result,
                    'analysis_types': analysis_types,
                    'period': period,
                    'show_continue_button': True,  # 新增：显示继续记录按钮
                }
                
                print(f"🎯 准备渲染模板 - 上下文键: {list(context.keys())}")
                return render(request, 'logs/ai_analysis_result.html', context)
                
            except Exception as e:
                print(f"❌ AI分析异常: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.error(request, f"AI分析服务出错: {str(e)}")
                return redirect('logs:ai_analysis')
    else:
        # 创建表单，如果有预选宠物则设置初始值
        initial_data = {}
        if initial_pet:
            initial_data['pet'] = initial_pet
        form = AIAnalysisForm(user=request.user, initial=initial_data)
    
    context = {
        'form': form,
        'initial_pet': initial_pet,
    }
    return render(request, 'logs/ai_analysis_form.html', context)


def convert_analysis_data_format(raw_data):
    """
    将get_analysis_data的输出转换为AI服务期望的格式
    """
    daily_records = raw_data.get('daily_records', [])
    
    # 统计数据
    weights = [r['weight'] for r in daily_records if r['weight']]
    lengths = [r['length'] for r in daily_records if r['length']]
    moods = [r['mood'] for r in daily_records if r['mood']]
    activities = [r['activity_level'] for r in daily_records if r['activity_level']]
    
    avg_weight = sum(weights) / len(weights) if weights else 0
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    
    mood_stats = dict(Counter(moods))
    activity_stats = dict(Counter(activities))
    
    # 转换为AI服务期望的格式
    converted_data = {
        'pet_info': {
            'name': raw_data['pet_info']['name'],
            'breed': raw_data['pet_info']['breed'],
            'age': raw_data['pet_info']['current_age_days'] / 365 if raw_data['pet_info']['current_age_days'] else 0,
            'gender': raw_data['pet_info']['gender'],
            'weight': weights[-1] if weights else 0  # 最新体重
        },        'logs_summary': {
            'date_range': raw_data['logs_summary']['date_range'],
            'total_logs': raw_data['logs_summary']['total_logs'],
            'avg_weight': avg_weight,
            'avg_length': avg_length,
            'latest_weight': weights[-1] if weights else 0,  # 最新体重
            'latest_length': lengths[-1] if lengths else 0,  # 最新身长
            'mood_stats': mood_stats,
            'activity_stats': activity_stats
        },
        'recent_logs': [
            {
                'date': record['date'],
                'weight': record['weight'] or 0,
                'length': record['length'] or 0,
                'mood': record['mood'] or '未知',
                'activity_level': record['activity_level'] or '未知',
                'food_intake': record['food_intake'] or 0,
                'water_intake': record['water_intake'] or 0,
                'notes': record['notes'] or '无'
            }
            for record in daily_records
        ]
    }
    
    return converted_data


def call_ai_analysis_service(analysis_data, analysis_types):
    """调用真实的AI分析服务"""
    return pet_log_analyzer.analyze_pet_logs(analysis_data, analysis_types)


@login_required
def log_data_export(request, pet_id):
    """导出宠物日志数据"""
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    
    # 获取查询参数
    days = int(request.GET.get('days', 30))
    format_type = request.GET.get('format', 'json')
    
    # 获取数据
    analysis_data = PetLog.objects.get_analysis_data(pet, days)
    
    if format_type == 'json':
        response = JsonResponse(analysis_data, json_dumps_params={'ensure_ascii': False, 'indent': 2})
        response['Content-Disposition'] = f'attachment; filename="{pet.name}_logs_{days}days.json"'
        return response
    
    # 可以在这里添加其他格式的导出支持（CSV, Excel等）
    return JsonResponse({'error': '不支持的导出格式'}, status=400)
