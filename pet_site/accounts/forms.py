from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

class PetConsultForm(forms.Form):
    PET_TYPES = [
        ('dog', '犬'),
        ('cat', '猫'),
        ('bird', '鸟'),
        ('rabbit', '兔子'),
        ('hamster', '仓鼠'),
        ('other', '其他')
    ]
    
    CONSULT_TYPES = [
        ('feeding', '日常饲养建议'),
        ('vaccine', '疫苗接种建议'),
        ('health', '健康与行为建议'),
        ('emergency', '紧急情况指引'),
        ('general', '综合咨询'),
    ]
    
    GENDER_CHOICES = [
        ('unknown', '未知'),
        ('male', '雄性'),
        ('female', '雌性')
    ]
    
    NEUTERED_CHOICES = [
        ('unknown', '不确定'),
        ('yes', '已绝育'),
        ('no', '未绝育')
    ]
    
    consult_type = forms.ChoiceField(
        label="咨询类型",
        choices=CONSULT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    pet_type = forms.ChoiceField(
        label="宠物种类",
        choices=PET_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    breed = forms.CharField(
        label="品种",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：金毛、英短、虎皮鹦鹉等'})
    )
    age = forms.IntegerField(
        label="年龄（岁）",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    weight = forms.FloatField(
        label="体重（kg）",
        min_value=0.1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    gender = forms.ChoiceField(
        label="性别",
        choices=GENDER_CHOICES,
        initial='unknown',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_gender'})
    )
    is_neutered = forms.ChoiceField(
        label="绝育状态",
        choices=NEUTERED_CHOICES,
        initial='unknown',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control neutered-field', 'id': 'id_is_neutered'})
    )
    specific_question = forms.CharField(
        label="具体问题（可选）",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3,
            'placeholder': '请描述您的具体问题或关注点...'
        })
    )
    
    # 紧急情况专用字段
    emergency_symptoms = forms.CharField(
        label="紧急症状描述",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control emergency-field', 
            'rows': 4,
            'placeholder': '请详细描述宠物当前的症状：\n- 行为异常（如：精神萎靡、不吃东西、呕吐、腹泻等）\n- 身体症状（如：呼吸急促、体温异常、抽搐等）\n- 发生时间和持续时间\n- 可能的诱因（如：误食、外伤等）'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 根据咨询类型动态调整字段要求
        if 'data' in kwargs and kwargs['data']:
            consult_type = kwargs['data'].get('consult_type')
            if consult_type == 'emergency':
                self.fields['emergency_symptoms'].required = True
                self.fields['specific_question'].required = False
            else:
                self.fields['emergency_symptoms'].required = False
