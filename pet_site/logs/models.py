from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import TimeStampedModel, SoftDeleteModel, LogChoices
from pets.models import Pet

# Create your models here.

class PetLogManager(models.Manager):
    """宠物日志自定义管理器"""
    
    def create_daily_log(self, pet, **kwargs):
        """创建日志，自动限制每个宠物最多300条记录"""
        # 检查该宠物今天是否已有记录
        today = timezone.now().date()
        if self.filter(pet=pet, date=today).exists():
            raise ValidationError(f"{pet.name}在{today}已有日志记录")
        
        # 检查该宠物的日志数量，如果超过300条则删除最早的
        log_count = self.filter(pet=pet).count()
        if log_count >= 300:
            # 删除最早的记录
            oldest_logs = self.filter(pet=pet).order_by('date')[:log_count - 299]
            for log in oldest_logs:
                log.delete()
        
        # 创建新记录
        kwargs['pet'] = pet
        kwargs['date'] = kwargs.get('date', today)
        return self.create(**kwargs)
    
    def get_recent_logs(self, pet, days=30):
        """获取最近N天的日志"""
        start_date = timezone.now().date() - timedelta(days=days)
        return self.filter(pet=pet, date__gte=start_date).order_by('-date')
    
    def get_analysis_data(self, pet, days=30):
        """获取用于AI分析的数据格式"""
        logs = self.get_recent_logs(pet, days)
        return {
            "pet_info": {
                "name": pet.name,
                "type": pet.get_pet_type_display(),
                "breed": str(pet.breed) if pet.breed else pet.custom_breed,
                "gender": pet.get_gender_display(),
                "is_neutered": pet.get_is_neutered_display(),
                "birth_date": pet.birth_date.isoformat() if pet.birth_date else None,
                "current_age_days": (timezone.now().date() - pet.birth_date).days if pet.birth_date else None
            },
            "logs_summary": {
                "total_logs": logs.count(),
                "date_range": f"{logs.last().date} 到 {logs.first().date}" if logs.exists() else "无记录",
                "analysis_period_days": days
            },
            "daily_records": [
                {
                    "date": log.date.isoformat(),
                    "weight": float(log.weight) if log.weight else None,
                    "length": float(log.length) if log.length else None,
                    "food_intake": float(log.food_intake) if log.food_intake else None,
                    "water_intake": float(log.water_intake) if log.water_intake else None,
                    "mood": log.get_mood_display() if log.mood else None,
                    "activity_level": log.get_activity_level_display() if log.activity_level else None,
                    "appetite": log.get_appetite_display() if log.appetite else None,
                    "daily_events": log.daily_events,
                    "age_at_record": log.age_at_record,
                    "temperature": float(log.temperature) if log.temperature else None,
                    "notes": log.notes
                }
                for log in logs
            ]
        }


class PetLog(TimeStampedModel, SoftDeleteModel):
    """宠物日志主表 - 支持完整的日常记录功能"""
    
    objects = PetLogManager()
    
    pet = models.ForeignKey(
        Pet, 
        on_delete=models.CASCADE,
        verbose_name="宠物",
        related_name="logs"
    )
    date = models.DateField(
        verbose_name="记录日期",
        help_text="记录的日期，每个宠物每天只能有一条记录"
    )
    
    # 基础生理指标
    weight = models.FloatField(
        null=True,
        blank=True,
        verbose_name="体重（公斤）",
        validators=[MinValueValidator(0.1), MaxValueValidator(500.0)],
        help_text="宠物当日体重，单位：公斤"
    )
    length = models.FloatField(
        null=True,
        blank=True,
        verbose_name="身长（厘米）",
        validators=[MinValueValidator(1.0), MaxValueValidator(500.0)],
        help_text="从鼻尖到尾尖的长度，单位：厘米"
    )
    age_at_record = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="记录时年龄（天）",
        validators=[MinValueValidator(0)],
        help_text="记录时宠物的实际年龄，单位：天"
    )
    temperature = models.FloatField(
        null=True,
        blank=True,
        verbose_name="体温（摄氏度）",
        validators=[MinValueValidator(30.0), MaxValueValidator(45.0)],
        help_text="体温，正常范围因宠物类型而异"
    )
    
    # 饮食相关
    food_intake = models.FloatField(
        null=True,
        blank=True,
        verbose_name="食物摄入量（克）",
        validators=[MinValueValidator(0.0)],
        help_text="当日总食物摄入量，包括主粮和零食"
    )
    water_intake = models.FloatField(
        null=True,
        blank=True,
        verbose_name="饮水量（毫升）",
        validators=[MinValueValidator(0.0)],
        help_text="当日总饮水量"
    )
    appetite = models.CharField(
        max_length=20,
        choices=LogChoices.APPETITE_CHOICES,
        blank=True,
        verbose_name="食欲状况"
    )
    
    # 行为和状态
    mood = models.CharField(
        max_length=20,
        choices=LogChoices.MOOD_CHOICES,
        blank=True,
        verbose_name="心情状态"
    )
    activity_level = models.CharField(
        max_length=20,
        choices=LogChoices.ACTIVITY_LEVEL_CHOICES,
        blank=True,
        verbose_name="活跃程度"
    )
    
    # 当日事件和备注
    daily_events = models.TextField(
        blank=True,
        verbose_name="当日事件",
        help_text="记录当日发生的特殊事件、行为变化、就医情况等"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="备注",
        help_text="其他需要记录的信息"
    )
    
    # 照片记录
    photos = models.JSONField(
        default=list,
        blank=True,
        verbose_name="照片列表",
        help_text="当日拍摄的照片文件路径列表"
    )
    
    class Meta:
        verbose_name = "宠物日志"
        verbose_name_plural = "宠物日志"
        ordering = ['-date', '-created_at']
        unique_together = [['pet', 'date']]
        indexes = [
            models.Index(fields=['pet', '-date']),
            models.Index(fields=['date']),
            models.Index(fields=['pet', 'weight']),
        ]
    
    def __str__(self):
        return f"{self.pet.name} - {self.date}"
    
    def save(self, *args, **kwargs):
        """保存时自动计算年龄"""
        if self.pet.birth_date and not self.age_at_record:
            self.age_at_record = (self.date - self.pet.birth_date).days
        super().save(*args, **kwargs)
    
    def clean(self):
        """数据验证"""
        # 检查日期不能是未来
        if self.date > timezone.now().date():
            raise ValidationError("记录日期不能是未来日期")
        
        # 检查该宠物今天是否已有记录（排除当前记录）
        existing = PetLog.objects.filter(pet=self.pet, date=self.date)
        if self.pk:
            existing = existing.exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError(f"{self.pet.name}在{self.date}已有日志记录")
    
    @property
    def age_display(self):
        """显示友好的年龄格式"""
        if not self.age_at_record:
            return "未知"
        days = self.age_at_record
        if days < 30:
            return f"{days}天"
        elif days < 365:
            months = days // 30
            return f"{months}个月"
        else:
            years = days // 365
            months = (days % 365) // 30
            if months > 0:
                return f"{years}岁{months}个月"
            return f"{years}岁"
    
    @property
    def growth_rate(self):
        """计算生长速度（相比上一条记录）"""
        previous_log = PetLog.objects.filter(
            pet=self.pet,
            date__lt=self.date,
            weight__isnull=False
        ).order_by('-date').first()
        
        if previous_log and self.weight and previous_log.weight:
            days_diff = (self.date - previous_log.date).days
            if days_diff > 0:
                weight_diff = self.weight - previous_log.weight
                return {
                    'weight_change': weight_diff,
                    'days_between': days_diff,
                    'daily_rate': weight_diff / days_diff
                }
        return None


class FeedingLog(TimeStampedModel):
    """喂食记录"""
    
    pet_log = models.ForeignKey(
        PetLog,
        on_delete=models.CASCADE,
        verbose_name="宠物日志",
        related_name="feeding_logs"
    )
    time = models.TimeField(
        verbose_name="喂食时间"
    )
    food_type = models.CharField(
        max_length=100,
        verbose_name="食物类型",
        help_text="主粮、零食、罐头等"
    )
    food_brand = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="食物品牌"
    )
    amount = models.CharField(
        max_length=50,
        verbose_name="食量",
        help_text="例如：一杯、50克、半罐等"
    )
    eaten_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True,
        verbose_name="进食比例（%）",
        help_text="宠物实际吃掉的比例"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="备注"
    )
    
    class Meta:
        verbose_name = "喂食记录"
        verbose_name_plural = "喂食记录"
        ordering = ['pet_log__date', 'time']
    
    def __str__(self):
        return f"{self.pet_log.pet.name} - {self.pet_log.date} {self.time} - {self.food_type}"


class ExerciseLog(TimeStampedModel):
    """运动记录"""
    
    pet_log = models.ForeignKey(
        PetLog,
        on_delete=models.CASCADE,
        verbose_name="宠物日志",
        related_name="exercise_logs"
    )
    start_time = models.TimeField(
        verbose_name="开始时间"
    )
    end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="结束时间"
    )
    exercise_type = models.CharField(
        max_length=50,
        verbose_name="运动类型",
        help_text="散步、跑步、游戏、训练等"
    )
    intensity = models.CharField(
        max_length=20,
        choices=LogChoices.EXERCISE_INTENSITY_CHOICES,
        default='medium',
        verbose_name="运动强度"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="运动地点"
    )
    distance = models.FloatField(
        null=True,
        blank=True,
        verbose_name="距离（公里）",
        validators=[MinValueValidator(0)]
    )
    notes = models.TextField(
        blank=True,
        verbose_name="备注"
    )
    
    class Meta:
        verbose_name = "运动记录"
        verbose_name_plural = "运动记录"
        ordering = ['pet_log__date', 'start_time']
    
    def __str__(self):
        return f"{self.pet_log.pet.name} - {self.pet_log.date} - {self.exercise_type}"
    
    @property
    def duration_minutes(self):
        """计算运动时长（分钟）"""
        if not self.end_time:
            return None
        from datetime import datetime, timedelta
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)
        
        # 处理跨天情况
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        
        duration = end_dt - start_dt
        return int(duration.total_seconds() / 60)


class HealthLog(TimeStampedModel):
    """健康记录"""
    
    pet_log = models.ForeignKey(
        PetLog,
        on_delete=models.CASCADE,
        verbose_name="宠物日志",
        related_name="health_logs"
    )
    log_type = models.CharField(
        max_length=30,
        choices=LogChoices.HEALTH_LOG_TYPES,
        verbose_name="记录类型"
    )
    time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="时间"
    )
    description = models.TextField(
        verbose_name="描述",
        help_text="详细描述观察到的情况"
    )
    severity = models.CharField(
        max_length=20,
        choices=LogChoices.SEVERITY_CHOICES,
        default='normal',
        verbose_name="严重程度"
    )
    action_taken = models.TextField(
        blank=True,
        verbose_name="采取的行动",
        help_text="如何处理该情况"
    )
    
    class Meta:
        verbose_name = "健康记录"
        verbose_name_plural = "健康记录"
        ordering = ['pet_log__date', 'time']
    
    def __str__(self):
        return f"{self.pet_log.pet.name} - {self.pet_log.date} - {self.get_log_type_display()}"


class MedicationLog(TimeStampedModel):
    """用药记录"""
    
    pet_log = models.ForeignKey(
        PetLog,
        on_delete=models.CASCADE,
        verbose_name="宠物日志",
        related_name="medication_logs"
    )
    time = models.TimeField(
        verbose_name="用药时间"
    )
    medication_name = models.CharField(
        max_length=200,
        verbose_name="药物名称"
    )
    dosage = models.CharField(
        max_length=100,
        verbose_name="剂量",
        help_text="例如：1片、5ml、半包等"
    )
    administration_method = models.CharField(
        max_length=50,
        verbose_name="给药方式",
        help_text="口服、注射、外用等"
    )
    prescribed_by = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="处方医生"
    )
    reason = models.CharField(
        max_length=200,
        verbose_name="用药原因"
    )
    side_effects = models.TextField(
        blank=True,
        verbose_name="副作用观察",
        help_text="用药后观察到的反应"
    )
    
    class Meta:
        verbose_name = "用药记录"
        verbose_name_plural = "用药记录"
        ordering = ['pet_log__date', 'time']
    
    def __str__(self):
        return f"{self.pet_log.pet.name} - {self.pet_log.date} - {self.medication_name}"


class LogAnalytics(models.Model):
    """日志分析数据 - 用于AI分析和趋势识别"""
    
    pet = models.OneToOneField(
        Pet,
        on_delete=models.CASCADE,
        verbose_name="宠物",
        related_name="analytics"
    )
    
    # 统计数据
    total_logs = models.IntegerField(
        default=0,
        verbose_name="总日志数"
    )
    last_log_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="最后记录日期"
    )
    
    # 健康趋势
    average_mood_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name="平均心情评分"
    )
    average_activity_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name="平均活跃度评分"
    )
    average_appetite_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name="平均食欲评分"
    )
    
    # 体重趋势
    latest_weight = models.FloatField(
        null=True,
        blank=True,
        verbose_name="最新体重"
    )
    weight_trend = models.CharField(
        max_length=20,
        choices=[
            ('increasing', '增长'),
            ('decreasing', '下降'),
            ('stable', '稳定'),
            ('unknown', '未知'),
        ],
        default='unknown',
        verbose_name="体重趋势"
    )
    
    # 异常提醒
    health_alerts = models.JSONField(
        default=list,
        blank=True,
        verbose_name="健康提醒",
        help_text="AI识别的健康异常提醒"
    )
    
    # 分析时间
    last_analyzed = models.DateTimeField(
        auto_now=True,
        verbose_name="最后分析时间"
    )
    
    class Meta:
        verbose_name = "日志分析"
        verbose_name_plural = "日志分析"
    
    def __str__(self):
        return f"{self.pet.name}的分析数据"
    
    def update_analytics(self):
        """更新分析数据"""
        from django.db.models import Avg, Max, Count
        from datetime import date, timedelta
        
        # 更新基础统计
        logs = self.pet.logs.filter(is_deleted=False)
        self.total_logs = logs.count()
        self.last_log_date = logs.aggregate(Max('date'))['date__max']
        
        # 计算最近30天的趋势
        recent_date = date.today() - timedelta(days=30)
        recent_logs = logs.filter(date__gte=recent_date)
        
        if recent_logs.exists():
            # 心情评分映射
            mood_scores = {
                'very_happy': 5, 'happy': 4, 'normal': 3, 
                'sad': 2, 'very_sad': 1, '': 3
            }
            # 活跃度评分映射
            activity_scores = {
                'very_active': 5, 'active': 4, 'normal': 3, 
                'inactive': 2, 'very_inactive': 1, '': 3
            }
            # 食欲评分映射
            appetite_scores = {
                'excellent': 5, 'good': 4, 'normal': 3, 
                'poor': 2, 'very_poor': 1, '': 3
            }
            
            # 计算平均分
            mood_avg = sum(mood_scores.get(log.mood, 3) for log in recent_logs) / recent_logs.count()
            activity_avg = sum(activity_scores.get(log.activity_level, 3) for log in recent_logs) / recent_logs.count()
            appetite_avg = sum(appetite_scores.get(log.appetite, 3) for log in recent_logs) / recent_logs.count()
            
            self.average_mood_score = round(mood_avg, 2)
            self.average_activity_score = round(activity_avg, 2)
            self.average_appetite_score = round(appetite_avg, 2)
            
            # 体重趋势分析
            weight_logs = recent_logs.filter(weight__isnull=False).order_by('date')
            if weight_logs.count() >= 2:
                weights = list(weight_logs.values_list('weight', flat=True))
                self.latest_weight = weights[-1]
                
                # 简单趋势判断
                if weights[-1] > weights[0] * 1.05:  # 增长超过5%
                    self.weight_trend = 'increasing'
                elif weights[-1] < weights[0] * 0.95:  # 下降超过5%
                    self.weight_trend = 'decreasing'
                else:
                    self.weight_trend = 'stable'
        
        self.save()
