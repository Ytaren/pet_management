# utils.py 
# AI将直接输出HTML格式的回复

def process_ai_advice(advice_text):
    """
    简单处理AI回复的HTML文本，确保安全性
    """
    if not advice_text:
        return ""
    
    # 简单的安全检查，移除可能的脚本标签
    import re
    
    # 移除任何潜在的脚本标签
    advice_text = re.sub(r'<script.*?</script>', '', advice_text, flags=re.DOTALL | re.IGNORECASE)
    advice_text = re.sub(r'<iframe.*?</iframe>', '', advice_text, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除onclick等事件属性
    advice_text = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', advice_text, flags=re.IGNORECASE)
    
    return advice_text.strip()


