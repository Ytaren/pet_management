from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from core.models import TimeStampedModel, ConsultationChoices
from pets.models import Pet

# Create your models here.

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
    
    def get_recent_by_user(self, user, days=30):
        """获取用户最近的咨询记录"""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(user=user, created_at__gte=cutoff_date)
    
    def get_by_consultation_type(self, consult_type):
        """按咨询类型获取记录"""
        return self.filter(consult_type=consult_type)


class ConsultationHistory(TimeStampedModel):
    """AI咨询历史记录模型"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name="用户",
        related_name="consultation_histories"
    )
    pet = models.ForeignKey(
        Pet, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="关联宠物",
        help_text="如果咨询是针对特定宠物的，可以关联宠物档案"
    )
    consult_type = models.CharField(
        max_length=20, 
        choices=ConsultationChoices.CONSULT_TYPES, 
        default='general',
        verbose_name="咨询类型"
    )
    
    # 如果没有关联宠物档案，则使用这些字段
    pet_type = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name="宠物类型",
        help_text="当没有关联宠物档案时填写"
    )
    breed = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="品种",
        help_text="当没有关联宠物档案时填写"
    )
    age = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="年龄（月）",
        help_text="当没有关联宠物档案时填写，单位为月"
    )
    weight = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="体重（公斤）",
        help_text="当没有关联宠物档案时填写"
    )
    gender = models.CharField(
        max_length=10, 
        choices=ConsultationChoices.GENDER_CHOICES, 
        default='unknown',
        blank=True,
        verbose_name="性别",
        help_text="当没有关联宠物档案时填写"
    )
    is_neutered = models.CharField(
        max_length=10, 
        choices=ConsultationChoices.NEUTERED_CHOICES, 
        default='unknown', 
        blank=True,
        verbose_name="绝育状态",
        help_text="当没有关联宠物档案时填写"
    )
    
    # 咨询内容
    specific_question = models.TextField(
        blank=True, 
        verbose_name="具体问题描述",
        help_text="详细描述您想咨询的问题"
    )
    emergency_symptoms = models.TextField(
        blank=True, 
        verbose_name="紧急症状描述",
        help_text="如果是紧急情况，请详细描述症状"
    )
    additional_info = models.TextField(
        blank=True, 
        verbose_name="补充信息",
        help_text="其他相关信息，如环境、饮食、行为变化等"
    )
    
    # AI 回复
    advice = models.TextField(
        verbose_name="AI建议",
        help_text="AI生成的建议和回复"
    )
    confidence_score = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="置信度分数",
        help_text="AI回复的置信度评分（0-1）"
    )
    
    # 用户反馈
    user_rating = models.IntegerField(
        null=True, 
        blank=True,
        choices=[(i, f"{i}星") for i in range(1, 6)],
        verbose_name="用户评分",
        help_text="用户对AI建议的评分（1-5星）"
    )
    user_feedback = models.TextField(
        blank=True,
        verbose_name="用户反馈",
        help_text="用户对AI建议的文字反馈"
    )
    
    # 系统字段
    session_id = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="会话ID",
        help_text="用于关联同一次对话的多轮咨询"
    )
    ai_model_version = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name="AI模型版本",
        help_text="生成回复的AI模型版本"
    )
    processing_time = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="处理时间（秒）",
        help_text="AI处理请求所用的时间"
    )
    
    # 添加自定义管理器
    objects = ConsultationHistoryManager()    
    class Meta:
        verbose_name = "AI咨询历史"
        verbose_name_plural = "AI咨询历史"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['consult_type']),
            models.Index(fields=['session_id']),
            models.Index(fields=['pet']),
        ]

    def __str__(self):
        pet_info = self.pet.name if self.pet else f"{self.pet_type}-{self.breed}"
        return f"{self.user.username}的{self.get_consult_type_display()}咨询 - {pet_info}"
    
    def get_advice_summary(self, max_length=100):
        """获取建议摘要"""
        import re
        # 移除HTML标签获取纯文本摘要
        clean_text = re.sub(r'<[^>]+>', '', self.advice)
        if len(clean_text) > max_length:
            return clean_text[:max_length] + '...'
        return clean_text
    
    @property
    def is_recent(self):
        """判断是否为最近的记录（7天内）"""
        if self.created_at is None:
            return False
        return timezone.now() - self.created_at <= timedelta(days=7)
    
    @property
    def pet_info(self):
        """获取宠物信息，优先使用关联的宠物档案"""
        if self.pet:
            return {
                'name': self.pet.name,
                'type': self.pet.pet_type,
                'breed': self.pet.display_breed,
                'age': self.pet.age_in_months,
                'weight': self.pet.weight,
                'gender': self.pet.gender,
                'is_neutered': self.pet.is_neutered,
            }
        else:
            return {
                'name': "未命名",
                'type': self.pet_type,
                'breed': self.breed,
                'age': self.age,
                'weight': self.weight,
                'gender': self.gender,
                'is_neutered': self.is_neutered,
            }
    
    def clean(self):
        """数据验证"""
        from django.core.exceptions import ValidationError
        
        # 如果没有关联宠物，必须填写基本信息
        if not self.pet:
            if not all([self.pet_type, self.breed]):
                raise ValidationError("当没有关联宠物档案时，必须填写宠物类型和品种")
        
        # 紧急咨询必须有症状描述
        if self.consult_type == 'emergency' and not self.emergency_symptoms:
            raise ValidationError("紧急咨询必须描述症状")


class ConsultationTemplate(TimeStampedModel):
    """咨询模板模型 - 用于存储常见问题的模板"""
    
    title = models.CharField(
        max_length=200,
        verbose_name="模板标题"
    )
    consult_type = models.CharField(
        max_length=20, 
        choices=ConsultationChoices.CONSULT_TYPES,
        verbose_name="咨询类型"
    )
    pet_type = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name="适用宠物类型",
        help_text="留空表示适用所有宠物类型"
    )
    template_content = models.TextField(
        verbose_name="模板内容",
        help_text="问题描述的模板文本"
    )
    suggested_response = models.TextField(
        blank=True,
        verbose_name="建议回复",
        help_text="针对此类问题的标准回复模板"
    )
    usage_count = models.IntegerField(
        default=0,
        verbose_name="使用次数"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用"
    )
    
    class Meta:
        verbose_name = "咨询模板"
        verbose_name_plural = "咨询模板"
        ordering = ['-usage_count', 'title']
        indexes = [
            models.Index(fields=['consult_type', 'is_active']),
            models.Index(fields=['pet_type']),
        ]
    
    def __str__(self):
        return self.title
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
