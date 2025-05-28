"""
宠物日志AI分析服务模块
基于DeepSeek API为宠物日志数据提供智能分析服务
"""

from openai import OpenAI
import json
from django.conf import settings
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class PetLogAIAnalyzer:
    """宠物日志AI分析器"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = "deepseek-reasoner"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
    
    def analyze_pet_logs(self, analysis_data: Dict, analysis_types: List[str]) -> Dict[str, Any]:
        """
        对宠物日志数据进行AI分析
        
        Args:
            analysis_data: 结构化的日志分析数据
            analysis_types: 分析类型列表 ['growth', 'health', 'behavior', 'nutrition', 'recommendations']
        
        Returns:
            分析结果字典
        """
        try:
            # 生成分析提示词
            prompt = self._generate_analysis_prompt(analysis_data, analysis_types)
            
            logger.info(f"发送AI分析请求，数据包含 {analysis_data.get('logs_summary', {}).get('total_logs', 0)} 条记录")
            
            # 调用DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的宠物健康分析师，请根据提供的数据进行详细分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                stream=False
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"AI响应成功，响应长度: {len(ai_response)}")
            
            # 解析AI响应并格式化
            return self._parse_ai_response(ai_response, analysis_data, analysis_types)
            
        except Exception as e:
            logger.error(f"DeepSeek API request error: {str(e)}")
            return self._get_fallback_result(analysis_data, analysis_types, f"AI分析服务异常: {str(e)}")
    
    def _generate_analysis_prompt(self, analysis_data: Dict, analysis_types: List[str]) -> str:
        """生成宠物日志分析的专业提示词"""
        
        # 获取基础信息
        pet_info = analysis_data.get('pet_info', {})
        logs_summary = analysis_data.get('logs_summary', {})
        recent_logs = analysis_data.get('recent_logs', [])
        
        # 构建宠物基本信息
        pet_info_text = f"""宠物基本信息：
- 姓名：{pet_info.get('name', '未知')}
- 品种：{pet_info.get('breed', '未知')}
- 年龄：{pet_info.get('age', '未知')}岁
- 性别：{pet_info.get('gender', '未知')}
- 体重：{pet_info.get('weight', '未知')}kg"""
          # 构建日志数据摘要
        summary_text = f"""日志数据概览：
- 记录期间：{logs_summary.get('date_range', '未知')}
- 总记录数：{logs_summary.get('total_logs', 0)}条
- 最新体重：{logs_summary.get('latest_weight', 0):.2f}kg
- 最新身长：{logs_summary.get('latest_length', 0):.2f}cm
- 主要心情状态：{logs_summary.get('mood_stats', {})}
- 活动水平分布：{logs_summary.get('activity_stats', {})}"""
          # 构建全部日志详情（选定时间内的所有记录）
        all_logs_text = f"分析期间全部日志记录（共{len(recent_logs)}条）：\n"
        for i, log in enumerate(recent_logs, 1):  # 发送所有选定时间内的日志记录
            all_logs_text += f"""{i}. 日期：{log.get('date', '未知')}
   - 体重：{log.get('weight', 0)}kg，身长：{log.get('length', 0)}cm
   - 心情：{log.get('mood', '未知')}，活动水平：{log.get('activity_level', '未知')}
   - 食物摄入：{log.get('food_intake', '未知')}，饮水量：{log.get('water_intake', '未知')}
   - 备注：{log.get('notes', '无')}
"""
        
        # 根据分析类型生成具体要求
        analysis_requirements = self._get_analysis_requirements(analysis_types)
        
        # 构建完整的分析提示词
        prompt = f"""你是一位专业的宠物健康分析师，请基于以下数据对宠物进行全面的健康分析：

{pet_info_text}

{summary_text}

{all_logs_text}

📋 分析要求：
{analysis_requirements}

⚠️ 重要输出格式要求：
请严格按照以下JSON格式返回分析结果，不要添加任何markdown格式或其他文本：

{{
    "summary": "基于数据的整体分析摘要",
    "analysis": {{
        {self._get_analysis_json_template(analysis_types)}
    }},
    "recommendations": [
        "具体建议1",
        "具体建议2",
        "具体建议3"
    ],
    "alerts": [
        "需要注意的问题1",
        "需要注意的问题2"
    ],
    "trends": {{
        "weight_trend": "体重变化趋势描述",
        "growth_trend": "生长发育趋势描述",
        "health_trend": "健康状况趋势描述",
        "behavior_trend": "行为模式趋势描述"
    }}
}}

请确保返回的是有效的JSON格式，不要包含任何其他内容。"""
        
        return prompt
    
    def _get_analysis_requirements(self, analysis_types: List[str]) -> str:
        """根据分析类型生成具体分析要求"""
        requirements = []
        
        if 'growth' in analysis_types:
            requirements.append("1. 生长发育分析：评估体重和身长的变化趋势，判断生长是否正常")
        
        if 'health' in analysis_types:
            requirements.append("2. 健康状况分析：基于心情、活动水平等指标评估整体健康状况")
        
        if 'behavior' in analysis_types:
            requirements.append("3. 行为模式分析：分析宠物的活动水平、心情变化等行为特征")
        
        if 'nutrition' in analysis_types:
            requirements.append("4. 营养状况分析：评估食物和饮水摄入情况，提供营养建议")
        
        if 'recommendations' in analysis_types:
            requirements.append("5. 护理建议：基于分析结果提供具体的护理和改善建议")
        
        return "\n".join(requirements)
    
    def _get_analysis_json_template(self, analysis_types: List[str]) -> str:
        """生成分析JSON模板"""
        template_parts = []
        
        if 'growth' in analysis_types:
            template_parts.append('"growth": "生长发育分析结果"')
        
        if 'health' in analysis_types:
            template_parts.append('"health": "健康状况分析结果"')
        
        if 'behavior' in analysis_types:
            template_parts.append('"behavior": "行为模式分析结果"')
        
        if 'nutrition' in analysis_types:
            template_parts.append('"nutrition": "营养状况分析结果"')
        
        return ",\n        ".join(template_parts)
    
    def _parse_ai_response(self, ai_response: str, analysis_data: Dict, analysis_types: List[str]) -> Dict[str, Any]:
        """解析AI响应并格式化为前端需要的数据结构"""
        try:
            # 尝试解析JSON响应
            ai_data = json.loads(ai_response)
            
            # 格式化为前端需要的结构
            result = {
                'summary': ai_data.get('summary', '分析完成'),
                'analysis': {
                    'growth': {
                        'description': ai_data.get('analysis', {}).get('growth', '无生长分析'),
                        'status': '正常'
                    },
                    'health': {
                        'description': ai_data.get('analysis', {}).get('health', '无健康分析'),
                        'status': '良好'
                    },
                    'behavior': {
                        'description': ai_data.get('analysis', {}).get('behavior', '无行为分析'),
                        'status': '稳定'
                    },
                    'nutrition': {
                        'description': ai_data.get('analysis', {}).get('nutrition', '无营养分析'),
                        'status': '均衡'
                    }
                },
                'recommendations': ai_data.get('recommendations', []),
                'alerts': ai_data.get('alerts', []),
                'trends': ai_data.get('trends', {}),
                'metadata': {
                    'analysis_date': '当前',
                    'total_logs': analysis_data.get('logs_summary', {}).get('total_logs', 0),
                    'analysis_types': analysis_types,
                    'ai_powered': True
                }
            }
            
            logger.info("AI响应解析成功")
            return result
            
        except json.JSONDecodeError:
            logger.warning("AI响应不是有效JSON，使用文本解析")
            # 如果不是JSON格式，直接使用文本内容
            return {
                'summary': 'AI分析已完成',
                'analysis': {
                    'comprehensive': {
                        'description': ai_response[:1000] + '...' if len(ai_response) > 1000 else ai_response,
                        'status': '完成'
                    }
                },
                'recommendations': ['根据AI分析结果进行调整'],
                'alerts': ['请关注AI分析中的重点内容'],
                'trends': {
                    'weight_trend': '请查看详细分析',
                    'growth_trend': '请查看详细分析',
                    'health_trend': '请查看详细分析',
                    'behavior_trend': '请查看详细分析'
                },
                'metadata': {
                    'analysis_date': '当前',
                    'total_logs': analysis_data.get('logs_summary', {}).get('total_logs', 0),
                    'analysis_types': analysis_types,
                    'ai_powered': True,
                    'fallback_reason': '响应格式为文本，已进行适配处理'
                },
                'raw_response': ai_response  # 保留原始响应
            }
    
    def _get_fallback_result(self, analysis_data: Dict, analysis_types: List[str], error_msg: str) -> Dict[str, Any]:
        """生成备用分析结果"""
        logs_summary = analysis_data.get('logs_summary', {})
        total_logs = logs_summary.get('total_logs', 0)
        
        if total_logs == 0:
            summary = "暂无日志数据进行分析"
            recommendations = ["请先记录宠物的日常数据"]
        else:
            summary = f"基于 {total_logs} 条记录的基础分析"
            recommendations = [
                "建议继续记录宠物的日常数据",
                "定期监测宠物的体重和健康状况",
                "保持规律的饮食和运动"
            ]
        
        return {
            'summary': summary,
            'analysis': {
                'basic': {
                    'description': f"记录了 {total_logs} 条数据，基础统计分析如下：\n- 平均体重：{logs_summary.get('avg_weight', 0):.2f}kg\n- 平均身长：{logs_summary.get('avg_length', 0):.2f}cm",
                    'status': '数据不足'
                }
            },
            'recommendations': recommendations,
            'alerts': [f"分析服务暂时不可用：{error_msg}"],
            'trends': {
                'weight_trend': '需要更多数据',
                'growth_trend': '需要更多数据',
                'health_trend': '需要更多数据',
                'behavior_trend': '需要更多数据'
            },
            'metadata': {
                'analysis_date': '当前',
                'total_logs': total_logs,
                'analysis_types': analysis_types,
                'ai_powered': False,
                'fallback_reason': f"AI服务暂时不可用：{error_msg}"
            }
        }


# 创建全局实例
pet_log_analyzer = PetLogAIAnalyzer()
