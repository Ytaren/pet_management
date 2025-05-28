from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import PetLog
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
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'max': timezone.now().date().isoformat()
                }
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
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': '其他备注信息...'
                }            ),
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
        
        # 修复编辑模式下的日期字段显示问题
        if self.instance and self.instance.pk:
            # 对于编辑现有记录，直接设置日期字段的value属性
            if self.instance.date:
                self.fields['date'].widget.attrs['value'] = self.instance.date.strftime('%Y-%m-%d')
                self.initial['date'] = self.instance.date

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
        initial=['growth', 'health', 'recommendations'],
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
