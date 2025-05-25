from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models



class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    
    def __str__(self):
        return self.username

class ConsultationHistoryManager(models.Manager):
    """自定义管理器，用于咨询历史记录的优化管理"""
    
    def cleanup_old_records(self, days=90):
        """清理超过指定天数的记录"""
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = self.filter(created_at__lt=cutoff_date).count()
        self.filter(created_at__lt=cutoff_date).delete()
        return deleted_count
    
    def limit_user_records(self, user, max_records=50):
        """限制用户最大记录数"""
        user_records = self.filter(user=user).order_by('-created_at')
        if user_records.count() > max_records:
            excess_records = user_records[max_records:]
            for record in excess_records:
                record.delete()
            return user_records.count() - max_records
        return 0

class ConsultationHistory(models.Model):
    CONSULT_TYPES = [
        ('feeding', '日常饲养建议'),
        ('vaccine', '疫苗接种建议'),
        ('health', '健康与行为建议'),
        ('emergency', '紧急情况指引'),
        ('general', '综合咨询'),
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
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    consult_type = models.CharField(max_length=20, choices=CONSULT_TYPES, default='general')
    pet_type = models.CharField(max_length=20)
    breed = models.CharField(max_length=100)
    age = models.IntegerField()
    weight = models.FloatField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unknown')
    is_neutered = models.CharField(max_length=10, choices=NEUTERED_CHOICES, default='unknown', blank=True)
    specific_question = models.TextField(blank=True, help_text="具体问题描述")
    emergency_symptoms = models.TextField(blank=True, help_text="紧急症状描述")
    advice = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 添加自定义管理器
    objects = ConsultationHistoryManager()

    class Meta:
        ordering = ['-created_at']  # 按时间倒序排列
        indexes = [
            models.Index(fields=['user', '-created_at']),  # 优化查询性能
            models.Index(fields=['created_at']),  # 优化清理操作
        ]

    def __str__(self):
        return f"{self.user.username}的{self.get_consult_type_display()}咨询记录"
    
    def get_advice_summary(self, max_length=100):
        """获取建议摘要"""
        # 移除HTML标签获取纯文本摘要
        import re
        clean_text = re.sub(r'<[^>]+>', '', self.advice)
        if len(clean_text) > max_length:
            return clean_text[:max_length] + '...'
        return clean_text
    
    @property
    def is_recent(self):
        """判断是否为最近的记录（7天内）"""
        return timezone.now() - self.created_at <= timedelta(days=7)