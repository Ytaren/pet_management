from django import forms
from django.core.exceptions import ValidationError
from .models import Pet, Breed
from core.models import PetChoices


class PetForm(forms.ModelForm):
    """宠物信息表单"""
    
    class Meta:
        model = Pet
        fields = [
            'name', 'pet_type', 'breed', 'custom_breed', 
            'birth_date', 'gender', 'is_neutered', 'weight',
            'photo', 'personality_notes', 'medical_notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入宠物姓名'
            }),
            'pet_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_pet_type'
            }),
            'breed': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_breed'
            }),
            'custom_breed': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '如果品种列表中没有对应品种，请填写自定义品种'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_neutered': forms.Select(attrs={
                'class': 'form-control'
            }),            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.1',
                'placeholder': '请输入体重（公斤）'
            }),
            'personality_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '描述宠物的性格特征、习惯、喜好等'
            }),
            'medical_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '记录宠物的病史、过敏史等医疗信息'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user
        
        # 设置字段显示名称
        self.fields['name'].label = '宠物姓名'
        self.fields['pet_type'].label = '宠物类型'
        self.fields['breed'].label = '品种'
        self.fields['custom_breed'].label = '自定义品种'
        self.fields['birth_date'].label = '出生日期'
        self.fields['gender'].label = '性别'
        self.fields['is_neutered'].label = '是否绝育'
        self.fields['weight'].label = '体重（公斤）'
        self.fields['personality_notes'].label = '性格描述'
        self.fields['medical_notes'].label = '医疗史'
        self.fields['photo'].label = '宠物照片'
        
        # 设置必填字段
        self.fields['name'].required = True
        self.fields['pet_type'].required = True
        self.fields['gender'].required = True
        
        # 初始化品种选择
        if 'pet_type' in self.data:
            try:
                pet_type = self.data.get('pet_type')
                self.fields['breed'].queryset = Breed.objects.filter(
                    pet_type=pet_type
                ).order_by('name')
            except (ValueError, TypeError):
                self.fields['breed'].queryset = Breed.objects.none()
        elif self.instance.pk:
            self.fields['breed'].queryset = Breed.objects.filter(
                pet_type=self.instance.pet_type
            ).order_by('name')
        else:
            self.fields['breed'].queryset = Breed.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        breed = cleaned_data.get('breed')
        custom_breed = cleaned_data.get('custom_breed')
        
        # 如果没有选择品种，必须填写自定义品种
        if not breed and not custom_breed:
            raise ValidationError('请选择品种或填写自定义品种')
        
        return cleaned_data
    
    def save(self, commit=True):
        pet = super().save(commit=False)
        if self.user:
            pet.owner = self.user
        if commit:
            pet.save()
        return pet


class PetFilterForm(forms.Form):
    """宠物筛选表单"""
    
    pet_type = forms.ChoiceField(
        choices=[('', '全部类型')] + PetChoices.PET_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    gender = forms.ChoiceField(
        choices=[('', '全部性别')] + PetChoices.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_neutered = forms.ChoiceField(
        choices=[('', '全部')] + PetChoices.NEUTERED_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索宠物姓名或品种'
        })
    )
