from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, verbose_name='手机号码')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, verbose_name='头像')
      # 基本个人信息
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    birth_date = models.DateField(null=True, blank=True, verbose_name='生日')
    location = models.CharField(max_length=100, blank=True, verbose_name='所在地')
    
    # 时间戳
    settings_updated_at = models.DateTimeField(auto_now=True, verbose_name='设置更新时间')
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'