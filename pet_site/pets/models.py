from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, SoftDeleteModel, PetChoices
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Breed(TimeStampedModel, SoftDeleteModel):
    """宠物品种模型"""
    name = models.CharField(
        max_length=100, 
        verbose_name="品种名称",
        help_text="宠物品种的中文名称"
    )
    name_en = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="英文名称",
        help_text="宠物品种的英文名称"
    )
    pet_type = models.CharField(
        max_length=20, 
        choices=PetChoices.PET_TYPES, 
        verbose_name="宠物类型"
    )
    description = models.TextField(
        blank=True, 
        verbose_name="品种描述",
        help_text="该品种的特征、性格等详细描述"
    )
    average_lifespan = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="平均寿命（年）",
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    average_weight_min = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="平均体重下限（公斤）",
        validators=[MinValueValidator(0.1)]
    )
    average_weight_max = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="平均体重上限（公斤）",
        validators=[MinValueValidator(0.1)]
    )
    
    class Meta:
        verbose_name = "宠物品种"
        verbose_name_plural = "宠物品种"
        ordering = ['pet_type', 'name']
        unique_together = [['name', 'pet_type']]
        indexes = [
            models.Index(fields=['pet_type', 'name']),
        ]
    
    def __str__(self):
        return f"{self.get_pet_type_display()} - {self.name}"
    
    def clean(self):
        """数据验证"""
        from django.core.exceptions import ValidationError
        if (self.average_weight_min and self.average_weight_max and 
            self.average_weight_min > self.average_weight_max):
            raise ValidationError("体重下限不能大于上限")


class Pet(TimeStampedModel, SoftDeleteModel):
    """宠物档案模型"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="主人",
        related_name="pets"
    )
    name = models.CharField(
        max_length=50, 
        verbose_name="宠物姓名"
    )
    pet_type = models.CharField(
        max_length=20, 
        choices=PetChoices.PET_TYPES, 
        verbose_name="宠物类型"
    )
    breed = models.ForeignKey(
        Breed, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="品种",
        help_text="如果没有对应品种，可以留空"
    )
    custom_breed = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="自定义品种",
        help_text="当品种列表中没有对应品种时填写"
    )
    birth_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="出生日期"
    )
    gender = models.CharField(
        max_length=10, 
        choices=PetChoices.GENDER_CHOICES, 
        default='unknown',
        verbose_name="性别"
    )
    is_neutered = models.CharField(
        max_length=10, 
        choices=PetChoices.NEUTERED_CHOICES, 
        default='unknown',
        verbose_name="绝育状态"
    )
    weight = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="体重（公斤）",
        validators=[MinValueValidator(0.1)],
        help_text="当前体重，单位为公斤"
    )
    microchip_number = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="芯片号码",
        help_text="宠物植入的微芯片编号"
    )
    photo = models.ImageField(
        upload_to='pets/photos/', 
        blank=True, 
        verbose_name="宠物照片"
    )
    medical_notes = models.TextField(
        blank=True, 
        verbose_name="医疗备注",
        help_text="特殊疾病、过敏史、用药记录等重要医疗信息"
    )
    personality_notes = models.TextField(
        blank=True, 
        verbose_name="性格备注",
        help_text="宠物的性格特征、习惯、喜好等"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="是否活跃",
        help_text="宠物是否还在主人身边（未走失、未去世等）"
    )
    
    class Meta:
        verbose_name = "宠物档案"
        verbose_name_plural = "宠物档案"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['pet_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.owner.username}的{self.name}"
    
    @property
    def age_in_months(self):
        """计算宠物月龄"""
        if not self.birth_date:
            return None
        from datetime import date
        today = date.today()
        return (today.year - self.birth_date.year) * 12 + (today.month - self.birth_date.month)
    
    @property
    def age_display(self):
        """格式化显示年龄"""
        months = self.age_in_months
        if months is None:
            return "未知"
        if months < 12:
            return f"{months}个月"
        years = months // 12
        remaining_months = months % 12
        if remaining_months == 0:
            return f"{years}岁"
        return f"{years}岁{remaining_months}个月"
    
    @property
    def display_breed(self):
        """显示品种名称"""
        if self.breed:
            return self.breed.name
        elif self.custom_breed:
            return self.custom_breed
        return "未知品种"
    
    def clean(self):
        """数据验证"""
        from django.core.exceptions import ValidationError
        from datetime import date
        
        if self.birth_date and self.birth_date > date.today():
            raise ValidationError("出生日期不能晚于今天")
        
        if not self.breed and not self.custom_breed:
            raise ValidationError("请选择品种或填写自定义品种")


class VaccinationRecord(TimeStampedModel):
    """疫苗接种记录模型"""
    pet = models.ForeignKey(
        Pet, 
        on_delete=models.CASCADE, 
        verbose_name="宠物",
        related_name="vaccination_records"
    )
    vaccine_name = models.CharField(
        max_length=100, 
        verbose_name="疫苗名称"
    )
    vaccination_date = models.DateField(
        verbose_name="接种日期"
    )
    next_due_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="下次接种日期"
    )
    veterinarian = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="接种医生"
    )
    clinic_name = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="诊所名称"
    )
    batch_number = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="疫苗批号"
    )
    notes = models.TextField(
        blank=True, 
        verbose_name="备注",
        help_text="接种后反应、特殊情况等"
    )
    
    class Meta:
        verbose_name = "疫苗接种记录"
        verbose_name_plural = "疫苗接种记录"
        ordering = ['-vaccination_date']
        indexes = [
            models.Index(fields=['pet', '-vaccination_date']),
            models.Index(fields=['next_due_date']),
        ]
    
    def __str__(self):
        return f"{self.pet.name} - {self.vaccine_name} ({self.vaccination_date})"
    
    @property
    def is_overdue(self):
        """判断是否过期需要接种"""
        if not self.next_due_date:
            return False
        from datetime import date
        return date.today() > self.next_due_date
