from django.utils.html import escape


def process_ai_advice(advice_text):
    """处理 AI 回复文本，避免脚本注入风险。"""
    if not advice_text:
        return ""

    # 统一转义为纯文本，前端由模板进行安全渲染。
    return escape(advice_text).strip()
