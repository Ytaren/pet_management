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
            growth_info = ""
            if obj.growth_rate and obj.growth_rate.get('weight_change'):
                change = obj.growth_rate['weight_change']
                if change > 0:
                    growth_info = f'<br><small style="color: green;">+{change:.1f}kg</small>'
                elif change < 0:
                    growth_info = f'<br><small style="color: orange;">{change:.1f}kg</small>'
            return format_html('{} kg{}', obj.weight, growth_info)
        return '-'
    weight_display.short_description = '体重'
    weight_display.admin_order_field = 'weight'
    
    def temperature_display(self, obj):
        """显示体温信息"""
        if obj.temperature:
            color = 'black'
            if obj.temperature < 38 or obj.temperature > 39.5:
                color = 'red'
            return format_html(
                '<span style="color: {};">{:.1f}°C</span>',
                color, obj.temperature
            )
        return '-'
    temperature_display.short_description = '体温'
    temperature_display.admin_order_field = 'temperature'
    
    def food_water_display(self, obj):
        """显示饮食信息"""
        parts = []
        if obj.food_intake:
            parts.append(f'食: {obj.food_intake}g')
        if obj.water_intake:
            parts.append(f'水: {obj.water_intake}ml')
        return '<br>'.join(parts) if parts else '-'
    food_water_display.short_description = '饮食'
    food_water_display.allow_tags = True
    
    def mood_activity_display(self, obj):
        """显示心情和活跃度"""
        parts = []
        if obj.mood:
            mood_colors = {
                'very_happy': 'green',
                'happy': 'lightgreen',
                'normal': 'gray',
                'sad': 'orange',
                'very_sad': 'red'
            }
            color = mood_colors.get(obj.mood, 'gray')
            parts.append(f'<span style="color: {color};">😊 {obj.get_mood_display()}</span>')
        
        if obj.activity_level:
            activity_colors = {
                'very_active': 'green',
                'active': 'lightgreen',
                'normal': 'gray',
                'inactive': 'orange',
                'very_inactive': 'red'
            }
            color = activity_colors.get(obj.activity_level, 'gray')
            parts.append(f'<span style="color: {color};">🏃 {obj.get_activity_level_display()}</span>')
        
        return mark_safe('<br>'.join(parts)) if parts else '-'
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
        self.message_user(request, f"已选择 {queryset.count()} 条日志进行导出")
    export_selected_logs.short_description = "导出选中的日志"
    
    def bulk_delete_logs(self, request, queryset):
        """批量删除日志"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"已删除 {count} 条日志记录")
    bulk_delete_logs.short_description = "批量删除选中的日志"
