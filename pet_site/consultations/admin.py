from django.contrib import admin
from .models import ConsultationHistory, ConsultationTemplate

# Register your models here.

@admin.register(ConsultationHistory)
class ConsultationHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'get_pet_name', 'consult_type', 'get_advice_summary', 
        'user_rating', 'confidence_score', 'created_at', 'is_recent'
    ]
    list_filter = [
        'consult_type', 'user_rating', 'created_at', 
        'pet__pet_type', 'ai_model_version'
    ]
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'pet__name', 'specific_question', 'advice'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'created_at', 'updated_at', 'is_recent', 
        'processing_time', 'confidence_score'
    ]
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user', 'pet', 'session_id')
        }),
        ('咨询类型', {
            'fields': ('consult_type',)
        }),
        ('宠物信息（未关联档案时使用）', {
            'fields': ('pet_type', 'breed', 'age', 'weight', 'gender', 'is_neutered'),
            'classes': ('collapse',)
        }),
        ('咨询内容', {
            'fields': ('specific_question', 'emergency_symptoms', 'additional_info')
        }),
        ('AI回复', {
            'fields': ('advice', 'confidence_score', 'ai_model_version', 'processing_time')
        }),
        ('用户反馈', {
            'fields': ('user_rating', 'user_feedback')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at', 'is_recent'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'pet')
    
    def get_pet_name(self, obj):
        return obj.pet.name if obj.pet else f"{obj.pet_type}-{obj.breed}"
    get_pet_name.short_description = '宠物'
    
    def is_recent(self, obj):
        return obj.is_recent
    is_recent.boolean = True
    is_recent.short_description = '最近记录'
    
    # 添加批量操作
    actions = ['cleanup_old_records']
    
    def cleanup_old_records(self, request, queryset):
        """批量清理旧记录"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=90)
        old_records = queryset.filter(created_at__lt=cutoff_date)
        count = old_records.count()
        old_records.delete()
        
        self.message_user(request, f"已清理 {count} 条90天前的记录")
    cleanup_old_records.short_description = "清理90天前的旧记录"


@admin.register(ConsultationTemplate)
class ConsultationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'consult_type', 'pet_type', 'usage_count', 
        'is_active', 'created_at'
    ]
    list_filter = ['consult_type', 'pet_type', 'is_active', 'created_at']
    search_fields = ['title', 'template_content']
    ordering = ['-usage_count', 'title']
    readonly_fields = ['created_at', 'updated_at', 'usage_count']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'consult_type', 'pet_type', 'is_active')
        }),
        ('模板内容', {
            'fields': ('template_content', 'suggested_response')
        }),
        ('使用统计', {
            'fields': ('usage_count',)
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # 添加批量操作
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"已启用 {queryset.count()} 个模板")
    make_active.short_description = "启用选中的模板"
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"已禁用 {queryset.count()} 个模板")
    make_inactive.short_description = "禁用选中的模板"
