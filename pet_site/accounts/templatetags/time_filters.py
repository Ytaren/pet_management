from django import template
from django.utils.timesince import timesince
import re

register = template.Library()

@register.filter
def clean_timesince(value):
    """
    自定义时间过滤器，将 Django timesince 的输出格式从 "1 日，10 小时" 转换为 "1日10小时"
    """
    if not value:
        return ""
    
    time_str = timesince(value)
    
    # 移除所有空格和逗号
    cleaned = re.sub(r'[，,\s]+', '', time_str)
    
    return cleaned
