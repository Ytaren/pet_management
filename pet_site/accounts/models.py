from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models



class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    
    def __str__(self):
        return self.username

from django.conf import settings
class ConsultationHistory(models.Model):
    CONSULT_TYPES = [
        ('feeding', '日常饲养建议'),
        ('vaccine', '疫苗接种建议'),
        ('health', '健康与行为建议'),
        ('emergency', '紧急情况指引'),
        ('general', '综合咨询'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    consult_type = models.CharField(max_length=20, choices=CONSULT_TYPES, default='general')
    pet_type = models.CharField(max_length=20)
    breed = models.CharField(max_length=100)
    age = models.IntegerField()
    weight = models.FloatField()
    specific_question = models.TextField(blank=True, help_text="具体问题描述")
    emergency_symptoms = models.TextField(blank=True, help_text="紧急症状描述")
    advice = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # 按时间倒序排列

    def __str__(self):
        return f"{self.user.username}的{self.get_consult_type_display()}咨询记录"