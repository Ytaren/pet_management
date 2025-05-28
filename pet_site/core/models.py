from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class TimeStampedModel(models.Model):
    """带时间戳的抽象基础模型"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    """软删除抽象模型"""
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="删除时间")
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """软删除方法"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        """恢复方法"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()

class ActiveManager(models.Manager):
    """过滤未删除记录的管理器"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

# 项目常量
class PetChoices:
    """宠物相关选择常量"""
    
    PET_TYPES = [
        ('cat', '猫'),
        ('dog', '狗'),
        ('rabbit', '兔子'),
        ('bird', '鸟'),
        ('fish', '鱼'),
        ('hamster', '仓鼠'),
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
    
    SIZE_CHOICES = [
        ('tiny', '超小型'),
        ('small', '小型'),
        ('medium', '中型'),
        ('large', '大型'),
        ('giant', '巨型'),
    ]

class ConsultationChoices:
    """咨询相关选择常量"""
    
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
    
    URGENCY_LEVELS = [
        ('low', '非紧急'),
        ('medium', '中等紧急'),
        ('high', '紧急'),
        ('critical', '危急'),
    ]

class LogChoices:
    """日志相关选择常量"""
    
    LOG_TYPES = [
        ('weight', '体重记录'),
        ('feeding', '喂食记录'),
        ('water_intake', '饮水记录'),
        ('exercise', '运动记录'),
        ('medication', '用药记录'),
        ('behavior', '行为记录'),
        ('health_check', '健康检查'),
    ]
    
    MOOD_CHOICES = [
        ('very_happy', '非常开心'),
        ('happy', '开心'),
        ('normal', '正常'),
        ('sad', '沮丧'),
        ('very_sad', '非常沮丧'),
    ]
    
    ACTIVITY_LEVEL_CHOICES = [
        ('very_active', '非常活跃'),
        ('active', '活跃'),
        ('normal', '正常'),
        ('inactive', '不活跃'),
        ('very_inactive', '非常不活跃'),
    ]
    
    APPETITE_CHOICES = [
        ('excellent', '极好'),
        ('good', '良好'),
        ('normal', '正常'),
        ('poor', '较差'),
        ('very_poor', '很差'),
    ]
    
    EXERCISE_INTENSITY_CHOICES = [
        ('low', '低强度'),
        ('medium', '中强度'),
        ('high', '高强度'),
    ]
    
    HEALTH_LOG_TYPES = [
        ('symptoms', '症状观察'),
        ('medication', '用药记录'),
        ('vaccination', '疫苗接种'),
        ('vet_visit', '就医记录'),
        ('grooming', '美容护理'),
        ('behavior_change', '行为变化'),
    ]
    
    SEVERITY_CHOICES = [
        ('normal', '正常'),
        ('mild', '轻微'),
        ('moderate', '中等'),
        ('severe', '严重'),
        ('critical', '危急'),
    ]
    
    UNIT_CHOICES = [
        ('kg', '千克'),
        ('g', '克'),
        ('ml', '毫升'),
        ('l', '升'),
        ('min', '分钟'),
        ('hour', '小时'),
    ]
