from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import PetLog, FeedingLog, ExerciseLog, HealthLog, MedicationLog
from pets.models import Pet

class PetLogForm(forms.ModelForm):
    """宠物日志表单"""
    
    class Meta:
        model = PetLog
        fields = [
            'pet', 'date', 'weight', 'length', 'temperature',
            'food_intake', 'water_intake', 'appetite',
            'mood', 'activity_level', 'daily_events', 'notes'
        ]
        widgets = {            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'max': timezone.now().date().isoformat()
                },
                format='%Y-%m-%d'
            ),
            'weight': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'placeholder': '例: 5.2'
                }
            ),
            'length': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'placeholder': '例: 45.5'
                }
            ),
            'temperature': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'placeholder': '例: 38.5'
                }
            ),
            'food_intake': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'placeholder': '例: 200'
                }
            ),
            'water_intake': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '1',
                    'placeholder': '例: 500'
                }
            ),
            'appetite': forms.Select(attrs={'class': 'form-control'}),
            'mood': forms.Select(attrs={'class': 'form-control'}),
            'activity_level': forms.Select(attrs={'class': 'form-control'}),
            'daily_events': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': '记录今天发生的特殊事件、行为变化等...'
                }
            ),
            'notes': forms.Textarea(                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': '其他备注信息...'
                }
            ),
            'pet': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        # 如果传入了用户，只显示该用户的宠物
        self.user = kwargs.pop('user', None)
        # 如果传入了宠物，设为默认选择
        self.initial_pet = kwargs.pop('initial_pet', None)
        super().__init__(*args, **kwargs)
        
        # 限制宠物选择范围
        if self.user:
            self.fields['pet'].queryset = Pet.objects.filter(owner=self.user)
        
        # 设置初始宠物
        if self.initial_pet:
            self.fields['pet'].initial = self.initial_pet
            # 如果指定了宠物，可以隐藏宠物选择字段
            self.fields['pet'].widget = forms.HiddenInput()
        
        # 设置日期字段的输入格式 - 与宠物表单保持一致
        self.fields['date'].input_formats = ['%Y-%m-%d']

    def get_initial(self):
        """获取表单初始值，确保编辑时所有字段正确显示"""
        initial = super().get_initial()
        
        if self.instance and self.instance.pk:
            # 编辑现有记录时，明确设置所有字段的初始值
            initial.update({
                'pet': self.instance.pet,
                'date': self.instance.date,
                'weight': self.instance.weight,
                'length': self.instance.length, 
                'temperature': self.instance.temperature,
                'food_intake': self.instance.food_intake,
                'water_intake': self.instance.water_intake,
                'appetite': self.instance.appetite,
                'mood': self.instance.mood,
                'activity_level': self.instance.activity_level,
                'daily_events': self.instance.daily_events,
                'notes': self.instance.notes,
            })
        else:
            # 新建记录时，设置默认日期为今天
            initial['date'] = timezone.now().date()
            
        return initial
    
    def clean_date(self):
        """验证日期"""
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError("记录日期不能是未来日期")
        return date
    
    def clean(self):
        """整体验证"""
        cleaned_data = super().clean()
        pet = cleaned_data.get('pet')
        date = cleaned_data.get('date')
        
        if pet and date:
            # 检查是否已存在该日期的记录（排除当前编辑的记录）
            existing = PetLog.objects.filter(pet=pet, date=date)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(f"{pet.name}在{date}已有日志记录")
        
        return cleaned_data


class PetLogFilterForm(forms.Form):
    """宠物日志过滤表单"""
    
    pet = forms.ModelChoiceField(
        queryset=Pet.objects.none(),
        required=False,
        empty_label="所有宠物",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        label="开始日期",
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )
    
    date_to = forms.DateField(
        required=False,
        label="结束日期",
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat()
            }
        )
    )
    
    mood = forms.ChoiceField(
        choices=[('', '所有心情')] + PetLog._meta.get_field('mood').choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    activity_level = forms.ChoiceField(
        choices=[('', '所有活跃度')] + PetLog._meta.get_field('activity_level').choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['pet'].queryset = Pet.objects.filter(owner=user)


class AIAnalysisForm(forms.Form):
    """AI分析请求表单"""
    
    pet = forms.ModelChoiceField(
        queryset=Pet.objects.none(),
        label="选择宠物",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    analysis_period = forms.ChoiceField(
        choices=[
            (7, '最近7天'),
            (14, '最近14天'),
            (30, '最近30天'),
            (60, '最近60天'),
            (90, '最近90天'),
        ],
        initial=30,
        label="分析周期",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    analysis_type = forms.MultipleChoiceField(
        choices=[
            ('growth', '生长发育分析'),
            ('health', '健康状况分析'),
            ('behavior', '行为模式分析'),
            ('nutrition', '营养状况分析'),
            ('recommendations', '护理建议'),
        ],
        initial=['growth', 'health', 'behavior', 'nutrition', 'recommendations'],
        label="分析类型",
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-check-input'}
        )
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['pet'].queryset = Pet.objects.filter(owner=user)
    
    def clean_analysis_period(self):
        """验证分析周期"""
        period = int(self.cleaned_data.get('analysis_period', 30))
        if period < 1 or period > 365:
            raise ValidationError("分析周期必须在1-365天之间")
        return period


# =============================================================================
# 详细记录子模块表单
# =============================================================================

class FeedingLogForm(forms.ModelForm):
    """喂食记录表单"""
    
    class Meta:
        model = FeedingLog
        fields = [
            'time', 'food_type', 'food_brand', 'amount', 
            'eaten_percentage', 'notes'
        ]
        widgets = {
            'time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                }
            ),
            'food_type': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例: 干粮、湿粮、零食、罐头',
                    'list': 'food-types'
                }
            ),
            'food_brand': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例: 皇家、希尔斯、渴望'
                }
            ),
            'amount': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例: 50克、半杯、1/4罐'
                }
            ),
            'eaten_percentage': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'max': '100',
                    'placeholder': '0-100'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': '其他备注信息...'
                }
            )
        }
    
    def clean_eaten_percentage(self):
        """验证进食比例"""
        percentage = self.cleaned_data.get('eaten_percentage')
        if percentage is not None and (percentage < 0 or percentage > 100):
            raise ValidationError("进食比例必须在0-100之间")
        return percentage


class ExerciseLogForm(forms.ModelForm):
    """运动记录表单"""
    
    class Meta:
        model = ExerciseLog
        fields = [
            'start_time', 'end_time', 'exercise_type', 'intensity',
            'location', 'distance', 'notes'
        ]
        widgets = {
            'start_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                }
            ),
            'end_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                }
            ),
            'exercise_type': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例: 散步、跑步、游戏、训练',
                    'list': 'exercise-types'
                }
            ),
            'intensity': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例: 小区公园、家中、宠物乐园'
                }
            ),
            'distance': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'placeholder': '例: 2.5 (公里)'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': '运动表现、特殊情况等...'
                }
            )
        }
    
    def clean(self):
        """验证运动时间"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            from datetime import datetime, timedelta
            start_dt = datetime.combine(datetime.today(), start_time)
            end_dt = datetime.combine(datetime.today(), end_time)
            
            # 处理跨天情况
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
            
            duration = end_dt - start_dt
            if duration.total_seconds() > 12 * 3600:  # 超过12小时
                raise ValidationError("运动时长不能超过12小时")
        
        return cleaned_data


class HealthLogForm(forms.ModelForm):
    """健康记录表单"""
    
    class Meta:
        model = HealthLog
        fields = [
            'log_type', 'time', 'description', 'severity', 'action_taken'
        ]
        widgets = {
            'log_type': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': '详细描述观察到的症状、行为或情况...'
                }
            ),
            'severity': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'action_taken': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': '采取的处理措施、用药情况、就医安排等...'
                }
            )
        }
    
    def clean_description(self):
        """验证描述内容"""
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 10:
            raise ValidationError("请提供至少10个字符的详细描述")
        return description


class MedicationLogForm(forms.ModelForm):
    """用药记录表单"""
    
    class Meta:
        model = MedicationLog
        fields = [
            'time', 'medication_name', 'dosage', 'administration_method',
            'prescribed_by', 'reason', 'side_effects'
        ]
        widgets = {
            'time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                }
            ),
            'medication_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例: 阿莫西林、布洛芬、驱虫药'
                }
            ),
            'dosage': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例: 1片、5ml、半包'
                }
            ),
            'administration_method': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例: 口服、注射、外用、滴耳',
                    'list': 'admin-methods'
                }
            ),
            'prescribed_by': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例: 张医生、某某宠物医院'
                }
            ),
            'reason': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例: 感冒、皮肤病、预防性用药'
                }
            ),
            'side_effects': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': '用药后观察到的反应、副作用等...'
                }
            )
        }
    
    def clean_medication_name(self):
        """验证药物名称"""
        name = self.cleaned_data.get('medication_name')
        if name and len(name.strip()) < 2:
            raise ValidationError("请输入有效的药物名称")
        return name
    
    def clean_dosage(self):
        """验证剂量信息"""
        dosage = self.cleaned_data.get('dosage')
        if dosage and len(dosage.strip()) < 1:
            raise ValidationError("请输入剂量信息")
        return dosage


# =============================================================================
# 复合表单 - 用于一次性添加多种记录
# =============================================================================

class DailyLogCompleteForm(forms.Form):
    """完整的每日记录表单 - 包含所有子记录类型"""
    
    # 基础日志信息 (必填)
    date = forms.DateField(
        label="记录日期",
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat()
            }
        ),
        initial=timezone.now().date
    )
    
    # 可选的详细记录标志
    include_feeding = forms.BooleanField(
        label="添加喂食记录",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    include_exercise = forms.BooleanField(
        label="添加运动记录", 
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    include_health = forms.BooleanField(
        label="添加健康记录",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    include_medication = forms.BooleanField(
        label="添加用药记录",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
