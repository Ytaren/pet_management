from django import forms
from core.models import ConsultationChoices

class PetConsultForm(forms.Form):
    """宠物咨询表单"""
    
    PET_TYPE_CHOICES = [
        ('dog', '狗'),
        ('cat', '猫'),
        ('bird', '鸟'),
        ('rabbit', '兔'),
        ('hamster', '仓鼠'),
        ('fish', '鱼'),
        ('reptile', '爬行动物'),
        ('other', '其他'),
    ]
    
    GENDER_CHOICES = [
        ('male', '雄性'),
        ('female', '雌性'),
        ('unknown', '未知')
    ]
    
    NEUTERED_CHOICES = [
        ('yes', '已绝育'),
        ('no', '未绝育'),
        ('unknown', '不确定')
    ]
    
    consult_type = forms.ChoiceField(
        choices=ConsultationChoices.CONSULT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='咨询类型'
    )
    
    pet_type = forms.ChoiceField(
        choices=PET_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='宠物类型'
    )
    
    breed = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '例如：金毛、英短、布偶猫等',
            'required': True
        }),
        label='品种'
    )
    
    age = forms.IntegerField(
        min_value=0,
        max_value=25,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '年龄（岁）',
            'required': True
        }),
        label='年龄'
    )
    
    weight = forms.FloatField(
        min_value=0.1,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '体重（公斤）',
            'step': '0.1',
            'required': True
        }),        label='体重'
    )
    
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='性别',
        required=False
    )
    
    is_neutered = forms.ChoiceField(
        choices=NEUTERED_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='绝育状态',
        required=False
    )
    
    specific_question = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': '请详细描述您的问题或宠物的具体情况...'
        }),
        label='具体问题',
        required=False
    )
    
    emergency_symptoms = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '请描述症状表现、持续时间、既往病史、可能诱因等...'
        }),
        label='紧急症状描述',
        required=False
    )
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and (age < 0 or age > 25):
            raise forms.ValidationError('年龄必须在0-25岁之间')
        return age
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and (weight < 0.1 or weight > 100):
            raise forms.ValidationError('体重必须在0.1-100公斤之间')
        return weight
    
    def clean_specific_question(self):
        question = self.cleaned_data.get('specific_question', '')
        if len(question) > 1000:
            raise forms.ValidationError('问题描述不能超过1000个字符')
        return question
    
    def clean_emergency_symptoms(self):
        symptoms = self.cleaned_data.get('emergency_symptoms', '')
        if len(symptoms) > 1000:
            raise forms.ValidationError('症状描述不能超过1000个字符')
        return symptoms
