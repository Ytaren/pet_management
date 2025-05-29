from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import PetLog

@admin.register(PetLog)
class PetLogAdmin(admin.ModelAdmin):
    """宠物日志管理界面"""
    
    list_display = [
        'pet_info', 'date', 'weight_display', 'temperature_display',
        'food_water_display', 'mood_activity_display', 'created_at'
    ]
    list_filter = [
        'pet__pet_type', 'date', 'mood', 'activity_level', 'appetite',
        'created_at', 'pet__owner'
    ]
    search_fields = [
        'pet__name', 'daily_events', 'notes', 'pet__owner__username'
    ]
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('pet', 'date')
        }),
        ('生理指标', {
            'fields': ('weight', 'length', 'temperature', 'age_at_record'),
            'classes': ('collapse',)
        }),
        ('饮食记录', {
            'fields': ('food_intake', 'water_intake', 'appetite'),
            'classes': ('collapse',)
        }),
        ('行为状态', {
            'fields': ('mood', 'activity_level'),
            'classes': ('collapse',)
        }),
        ('事件和备注', {
            'fields': ('daily_events', 'notes'),
            'classes': ('collapse',)
        }),
        ('照片记录', {
            'fields': ('photos',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['age_at_record']
    
    def pet_info(self, obj):
        """显示宠物信息"""
        return format_html(
            '<strong>{}</strong><br><small>{} | {}</small>',
            obj.pet.name,
            obj.pet.get_pet_type_display(),
            obj.pet.owner.username
        )
    pet_info.short_description = '宠物信息'
    pet_info.admin_order_field = 'pet__name'
    
    def weight_display(self, obj):
        """显示体重信息"""
        if obj.weight:
            base_weight = str(obj.weight) + ' kg'
            growth_info = ''
            
            # 检查是否有增长率数据
            if hasattr(obj, 'growth_rate') and obj.growth_rate and obj.growth_rate.get('weight_change'):
                try:
                    change = float(obj.growth_rate['weight_change'])
                    if change > 0:
                        growth_info = '<br><small style="color: green;">+{:.1f}kg</small>'.format(change)
                    elif change < 0:
                        growth_info = '<br><small style="color: orange;">{:.1f}kg</small>'.format(change)
                except (ValueError, TypeError):
                    growth_info = ''
            
            return mark_safe(base_weight + growth_info)
        return '-'
    weight_display.short_description = '体重'
    weight_display.admin_order_field = 'weight'
    
    def temperature_display(self, obj):
        """显示体温信息"""
        if obj.temperature:
            try:
                temp = float(obj.temperature)
                color = 'black'
                if temp < 38 or temp > 39.5:
                    color = 'red'
                return format_html(
                    '<span style="color: {};">{:.1f}°C</span>',
                    color, temp
                )
            except (ValueError, TypeError):
                return str(obj.temperature) + '°C'
        return '-'
    temperature_display.short_description = '体温'
    temperature_display.admin_order_field = 'temperature'
    
    def food_water_display(self, obj):
        """显示饮食信息"""
        parts = []
        if obj.food_intake:
            parts.append('食: {}g'.format(obj.food_intake))
        if obj.water_intake:
            parts.append('水: {}ml'.format(obj.water_intake))
        
        if parts:
            return mark_safe('<br>'.join(parts))
        return '-'
    food_water_display.short_description = '饮食'
    
    def mood_activity_display(self, obj):
        """显示心情和活跃度"""
        parts = []
        
        # 处理心情显示
        if obj.mood:
            mood_colors = {
                'very_happy': 'green',
                'happy': 'lightgreen',
                'normal': 'gray',
                'sad': 'orange',
                'very_sad': 'red'
            }
            color = mood_colors.get(obj.mood, 'gray')
            mood_text = '<span style="color: {};">😊 {}</span>'.format(
                color, obj.get_mood_display()
            )
            parts.append(mood_text)
        
        # 处理活跃度显示
        if obj.activity_level:
            activity_colors = {
                'very_active': 'green',
                'active': 'lightgreen',
                'normal': 'gray',
                'inactive': 'orange',
                'very_inactive': 'red'
            }
            color = activity_colors.get(obj.activity_level, 'gray')
            activity_text = '<span style="color: {};">🏃 {}</span>'.format(
                color, obj.get_activity_level_display()
            )
            parts.append(activity_text)
        
        if parts:
            return mark_safe('<br>'.join(parts))
        return '-'
    mood_activity_display.short_description = '状态'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('pet', 'pet__owner')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """限制宠物选择范围"""
        if db_field.name == "pet":
            if not request.user.is_superuser:
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    owner=request.user
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """保存时的额外处理"""
        if not change and not request.user.is_superuser:
            # 非超级用户只能为自己的宠物添加日志
            if obj.pet.owner != request.user:
                raise PermissionError("您只能为自己的宠物添加日志")
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        """检查修改权限"""
        if obj and not request.user.is_superuser:
            return obj.pet.owner == request.user
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """检查删除权限"""
        if obj and not request.user.is_superuser:
            return obj.pet.owner == request.user
        return super().has_delete_permission(request, obj)
    
    actions = ['export_selected_logs', 'bulk_delete_logs']
    
    def export_selected_logs(self, request, queryset):
        """批量导出日志"""
        # 这里可以实现导出逻辑
        self.message_user(request, "已选择 {} 条日志进行导出".format(queryset.count()))
    export_selected_logs.short_description = "导出选中的日志"
    
    def bulk_delete_logs(self, request, queryset):
        """批量删除日志"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, "已删除 {} 条日志记录".format(count))
    bulk_delete_logs.short_description = "批量删除选中的日志"
