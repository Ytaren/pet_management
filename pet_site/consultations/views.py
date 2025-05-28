from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.conf import settings
import requests
import re

from .models import ConsultationHistory
from .forms import PetConsultForm

# Create your views here.

def validate_pet_data(pet_type, age, weight, specific_question, emergency_symptoms):
    """数据逻辑安全审查，防止不当输入"""
    
    # 合并所有文本内容进行检查
    text_to_check = f"{pet_type} {specific_question} {emergency_symptoms}".lower()
    
    # 1. 年龄和体重逻辑检查
    if age < 0 or age > 25:
        return {
            'is_valid': False,
            'error_message': '年龄范围异常，宠物年龄应在0-25岁之间'
        }
    
    if weight < 0.1 or weight > 100:
        return {
            'is_valid': False,
            'error_message': '体重范围异常，请输入合理的宠物体重（0.1-100kg）'
        }
    
    # 2. 中毒关键词检测
    poison_keywords = [
        '巧克力', '葡萄', '洋葱', '大蒜', '木糖醇', '咖啡因', '酒精', '鳄梨', '坚果',
        'chocolate', 'grape', 'onion', 'garlic', 'xylitol', 'caffeine', 'alcohol', 'avocado',
        '误食', '中毒', '吃了', '咬了', 'poison', 'toxic', 'ate', 'swallow'
    ]
    
    is_emergency_poison = any(keyword in text_to_check for keyword in poison_keywords)
    
    # 3. 伤害性内容检测
    harmful_keywords = [
        '打', '踢', '摔', '扔', '虐待', '伤害', '报复', '惩罚', '折磨',
        'beat', 'kick', 'throw', 'abuse', 'hurt', 'punish', 'torture'
    ]
    
    for keyword in harmful_keywords:
        if keyword in text_to_check:
            return {
                'is_valid': False,
                'error_message': '⚠️ 检测到可能的伤害性内容。<br><br>💚 爱护宠物提示：<br>• 宠物需要关爱和耐心护理<br>• 如遇行为问题，建议咨询专业训练师<br>• 任何暴力行为都会伤害宠物身心健康<br><br>本平台提倡科学、人性化的宠物护理方式。'
            }
    
    # 4. 医疗误导内容检测
    medical_keywords = [
        '人药', '人类药物', '感冒药', '止痛药', '抗生素', '激素',
        'human medicine', 'painkiller', 'antibiotic', 'steroid'
    ]
    
    for keyword in medical_keywords:
        if keyword in text_to_check:
            return {
                'is_valid': False,
                'error_message': '🚨 用药安全警告<br><br>⚠️ 人类药物对宠物可能致命！<br><br>✅ 正确做法：<br>• 仅使用兽医处方药物<br>• 严格按照兽医指导用药<br>• 紧急情况下联系宠物医院<br><br>本平台不提供用药指导，请咨询专业兽医。'
            }
    
    # 5. 遗弃/转让内容检测
    abandon_keywords = [
        '不想要', '送人', '扔掉', '遗弃', '卖掉', '处理掉', '摆脱',
        'abandon', 'get rid of', 'throw away', 'sell', 'give away', 'dispose'
    ]
    
    for keyword in abandon_keywords:
        if keyword in text_to_check:
            return {
                'is_valid': False,
                'error_message': '❌ 检测到不当内容。<br><br>如需宠物重新安置，请联系：<br>• 当地动物救助中心<br>• 宠物领养平台<br>• 动物保护协会<br><br>本平台仅提供宠物护理健康咨询。'
            }
    
    # 6. 其他危险行为检测
    other_dangerous = [
        '实验', '解剖', '吃掉', '煮', '炖', '烤', '屠宰',
        'kill', 'murder', 'abuse', 'torture', 'harm', 'poison', 'abandon'
    ]
    
    for keyword in other_dangerous:
        if keyword in text_to_check:
            return {
                'is_valid': False,
                'error_message': '⚠️ 检测到不当内容，本平台仅提供正当的宠物护理咨询服务。'
            }
    
    # 🔍 异常文本模式检测
    suspicious_patterns = [
        r'[0-9]{10,}',  # 超长数字串
        r'(.)\1{10,}',  # 重复字符超过10次
        r'[^a-zA-Z0-9\u4e00-\u9fa5\s\.,!?，。！？、；：""''（）]+',  # 异常字符
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text_to_check):
            return {
                'is_valid': False,
                'error_message': '检测到异常输入格式，请使用规范的文字描述宠物问题'
            }
    
    # 文本长度检查
    if len(text_to_check) > 2000:
        return {
            'is_valid': False,
            'error_message': '输入文本过长，请精简描述后重新提交'
        }
    
    return {'is_valid': True, 'error_message': '', 'is_emergency_poison': is_emergency_poison}


@login_required
def pet_consult_view(request):
    """宠物咨询视图"""
    advice = None
    if request.method == 'POST':
        form = PetConsultForm(request.POST)
        if form.is_valid():
            response = None
            
            try:
                # 根据咨询类型生成不同的提示词
                consult_type = form.cleaned_data['consult_type']
                pet_type = form.cleaned_data['pet_type']
                breed = form.cleaned_data['breed']
                age = form.cleaned_data['age']
                weight = form.cleaned_data['weight']
                gender = form.cleaned_data['gender']
                is_neutered = form.cleaned_data.get('is_neutered', 'unknown')
                specific_question = form.cleaned_data.get('specific_question', '')
                emergency_symptoms = form.cleaned_data.get('emergency_symptoms', '')
                
                # 构建专业的AI提示词
                prompt = generate_prompt(consult_type, pet_type, breed, age, weight, gender, is_neutered, specific_question, emergency_symptoms)
                
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7
                    },
                    timeout=100
                )
                
                if response.status_code == 200:
                    advice = response.json().get('choices', [{}])[0].get('message', {}).get('content', '无返回内容')
                else:
                    advice = f"API请求失败，状态码：{response.status_code}。请检查您的API密钥配置。"
                
                # 保存咨询记录
                ConsultationHistory.objects.create(
                    user=request.user,
                    consult_type=consult_type,
                    pet_type=pet_type,
                    breed=breed,
                    age=age,
                    weight=weight,
                    gender=gender,
                    is_neutered=is_neutered,
                    specific_question=specific_question,
                    emergency_symptoms=emergency_symptoms,
                    advice=advice
                )
                
                # 自动限制用户记录数量（保留最近150条）
                ConsultationHistory.objects.limit_user_records(request.user, max_records=150)
                    
            except requests.exceptions.RequestException as e:
                advice = f"网络请求异常：{str(e)}"
            except Exception as e:
                advice = f"处理错误：{str(e)}"
    else:
        form = PetConsultForm()

    return render(request, 'consultations/pet_consult.html', {
        'form': form,
        'advice': advice
    })


def generate_prompt(consult_type, pet_type, breed, age, weight, gender, is_neutered, specific_question, emergency_symptoms=''):
    """根据咨询类型生成专业的AI提示词，包含安全审查机制"""
    
    # 🔒 数据逻辑安全审查
    validation_result = validate_pet_data(pet_type, age, weight, specific_question, emergency_symptoms)
    if not validation_result['is_valid']:
        # 错误消息已经是HTML格式，不需要额外转换
        error_message = validation_result['error_message']
        return f"""
<div class="alert alert-warning border-warning">
<div class="d-flex align-items-center mb-3">
<i class="fas fa-exclamation-triangle text-warning me-2" style="font-size: 1.5em;"></i>
<h4 class="mb-0">⚠️ 内容检测提示</h4>
</div>
<div class="alert alert-light border-left-warning">
<strong>检测问题：</strong><br>
<div class="mt-2">{error_message}</div>
</div>

<hr class="my-4">

<h5 class="text-primary">📋 正确咨询示例</h5>
<div class="row mt-3">
<div class="col-md-6">
<div class="card border-success">
<div class="card-body">
<h6 class="card-title text-success">🐱 猫咪咨询</h6>
<ul class="list-unstyled">
<li>• 年龄：1-20岁</li>
<li>• 体重：2-10kg</li>
<li>• 示例：3岁英短猫食欲不振怎么办？</li>
</ul>
</div>
</div>
</div>
<div class="col-md-6">
<div class="card border-info">
<div class="card-body">
<h6 class="card-title text-info">🐶 狗狗咨询</h6>
<ul class="list-unstyled">
<li>• 年龄：1-18岁</li>
<li>• 体重：1-80kg</li>
<li>• 示例：金毛犬关节护理注意事项</li>
</ul>
</div>
</div>
</div>
</div>

<div class="alert alert-info mt-4">
<i class="fas fa-lightbulb me-2"></i>
<strong>💡 建议：</strong>请修改为宠物健康护理相关的正当问题，或联系平台客服获取帮助。
</div>
</div>
"""
    
    # 🚨 检查是否为紧急中毒情况
    is_emergency_poison = validation_result.get('is_emergency_poison', False)
    
    # 性别显示转换
    gender_display = {
        'male': '雄性',
        'female': '雌性', 
        'unknown': '未知'
    }.get(gender, '未知')
    
    # 绝育状态显示转换
    neutered_display = {
        'yes': '已绝育',
        'no': '未绝育',
        'unknown': '不确定'
    }.get(is_neutered, '不确定')
    
    # 强调品种特性的基础信息
    base_info = f"""
宠物信息：
- 种类：{pet_type}
- 品种：{breed}（⚠️ 重点：请特别关注{breed}品种的独特特性和需求）
- 年龄：{age}岁
- 体重：{weight}kg
- 性别：{gender_display}
- 绝育状态：{neutered_display}
"""
    if specific_question:
        base_info += f"- 具体问题：{specific_question}\n"
    
    if emergency_symptoms:
        base_info += f"- 🚨 紧急症状：{emergency_symptoms}\n"
    
    # 添加品种差异化分析的重点提示
    breed_emphasis = f"""
🎯 请务必针对{breed}品种的特殊性进行分析：
- {breed}品种的遗传特性和常见问题
- {breed}品种的体型、活动需求和性格特点
- {breed}品种的饮食特殊需求和禁忌
- {breed}品种的易感疾病和预防措施
- {breed}品种的寿命周期和年龄相关护理重点
"""
    
    # 根据咨询类型生成不同的提示词
    prompts = {
        'feeding': f"""作为专业的宠物营养师，请为以下{breed}品种宠物制定专业的饮食方案：
{base_info}
{breed_emphasis}

⚠️ 重要：请严格按照HTML格式输出，不要使用markdown语法！

请按以下HTML模板输出：

<h3>🍽️ {breed}品种营养配餐方案</h3>
<p>专为{age}岁{breed}({weight}kg)定制的营养方案：</p>
<ul>
<li><strong>主食建议：</strong>适合{breed}品种的主食类型和品牌推荐</li>
<li><strong>食物分量：</strong>基于{weight}kg体重的每日精确食量</li>
<li><strong>喂食频次：</strong>适合{age}岁{breed}的喂食时间表</li>
<li><strong>品种禁忌：</strong>{breed}品种绝对不能食用的食物清单</li>
</ul>

<h3>💊 {breed}品种营养补充</h3>
<ul>
<li><strong>必需营养素：</strong>{breed}品种特别需要的维生素和矿物质</li>
<li><strong>年龄营养：</strong>{age}岁{breed}的年龄特定营养需求</li>
<li><strong>体重管理：</strong>维持{weight}kg理想体重的营养策略</li>
<li><strong>季节调整：</strong>{breed}品种的季节性饮食调整</li>
</ul>

<h3>🚫 {breed}品种饮食安全</h3>
<ul>
<li><strong>中毒预防：</strong>{breed}品种容易中毒的食物和预防措施</li>
<li><strong>过敏风险：</strong>{breed}品种常见的食物过敏源</li>
<li><strong>消化特点：</strong>{breed}品种的消化系统特性和注意事项</li>
<li><strong>紧急处理：</strong>误食有害食物后的应急措施</li>
</ul>

<div class="alert alert-info">
<strong>品种提示：</strong>{breed}品种有其独特的营养需求，请严格按照该品种的饮食特点制定方案，必要时咨询专业宠物营养师。
</div>""",

        'vaccine': f"""作为宠物免疫专家，请为以下{breed}品种宠物制定疫苗接种方案：
{base_info}
{breed_emphasis}

⚠️ 重要：请严格按照HTML格式输出，不要使用markdown语法！

请按以下HTML模板输出：

<h3>💉 {breed}品种疫苗接种计划</h3>
<p>为{age}岁{breed}制定的个性化疫苗方案：</p>
<ul>
<li><strong>核心疫苗：</strong>{breed}品种必须接种的核心疫苗类型和时间</li>
<li><strong>年龄疫苗：</strong>适合{age}岁{breed}的当前疫苗需求</li>
<li><strong>加强针：</strong>{breed}品种的疫苗加强接种时间表</li>
<li><strong>品种风险：</strong>{breed}品种特别需要预防的疾病疫苗</li>
</ul>

<h3>🛡️ {breed}品种免疫保护</h3>
<ul>
<li><strong>疾病预防：</strong>{breed}品种易感疾病的疫苗保护策略</li>
<li><strong>免疫效果：</strong>评估{breed}品种疫苗免疫效果的方法</li>
<li><strong>抗体检测：</strong>{breed}品种建议的抗体检测频率</li>
<li><strong>群体免疫：</strong>{breed}品种在群养环境下的免疫考虑</li>
</ul>

<h3>⚠️ {breed}品种疫苗注意事项</h3>
<ul>
<li><strong>接种前准备：</strong>{breed}品种疫苗接种前的健康评估</li>
<li><strong>不良反应：</strong>{breed}品种可能的疫苗不良反应和处理</li>
<li><strong>接种间隔：</strong>{breed}品种疫苗之间的最佳间隔时间</li>
<li><strong>特殊情况：</strong>{breed}品种在疾病或应激状态下的疫苗调整</li>
</ul>

<div class="alert alert-warning">
<strong>专业提醒：</strong>{breed}品种有其特殊的免疫特点，请务必在专业兽医指导下制定和执行疫苗计划，不要自行调整疫苗方案。
</div>""",

        'health': f"""作为{breed}品种健康专家，请为以下宠物提供全面的健康管理建议：
{base_info}
{breed_emphasis}

⚠️ 重要：请严格按照HTML格式输出，不要使用markdown语法！

请按以下HTML模板输出：

<h3>🏃‍♂️ {breed}品种运动健康</h3>
<p>基于{breed}品种特性的运动健康方案：</p>
<ul>
<li><strong>运动需求：</strong>{breed}品种的每日运动量和强度建议</li>
<li><strong>年龄调整：</strong>{age}岁{breed}的运动方案调整</li>
<li><strong>体重管理：</strong>维持{weight}kg健康体重的运动策略</li>
<li><strong>关节保护：</strong>{breed}品种的关节健康运动方案</li>
</ul>

<h3>💚 {breed}品种疾病预防</h3>
<ul>
<li><strong>遗传疾病：</strong>{breed}品种常见遗传性疾病的预防</li>
<li><strong>年龄疾病：</strong>{age}岁{breed}需要重点预防的疾病</li>
<li><strong>环境疾病：</strong>{breed}品种对环境因素敏感的疾病预防</li>
<li><strong>早期发现：</strong>{breed}品种疾病的早期症状识别</li>
</ul>

<h3>🧠 {breed}品种行为健康</h3>
<ul>
<li><strong>心理健康：</strong>{breed}品种的心理健康维护方法</li>
<li><strong>社交需求：</strong>{breed}品种的社交和刺激需求</li>
<li><strong>压力管理：</strong>{breed}品种的压力识别和缓解方法</li>
<li><strong>认知训练：</strong>适合{breed}品种智力水平的认知训练</li>
</ul>

<h3>🔍 {breed}品种定期检查</h3>
<ul>
<li><strong>体检频率：</strong>{breed}品种建议的健康检查频率</li>
<li><strong>专项检查：</strong>{breed}品种需要的特殊检查项目</li>
<li><strong>居家监测：</strong>在家监测{breed}品种健康状况的方法</li>
<li><strong>记录管理：</strong>{breed}品种健康档案的建立和管理</li>
</ul>

<div class="alert alert-success">
<strong>健康提示：</strong>{breed}品种有其独特的健康管理需求，建议建立完整的健康档案，定期与熟悉该品种的兽医进行健康评估。
</div>""",

        'emergency': f"""🚨 {breed}品种紧急情况处理指南
{base_info}
{breed_emphasis}

⚠️ 重要：这是紧急情况指导，请在联系专业兽医的同时参考以下建议！

⚠️ 重要：请严格按照HTML格式输出，不要使用markdown语法！

请按以下HTML模板输出：

<h3>🚨 立即行动指南</h3>
<p>基于{breed}品种特性的紧急处理步骤：</p>
<ul>
<li><strong>生命体征检查：</strong>检查{breed}品种的关键生命体征</li>
<li><strong>安全处理：</strong>确保{breed}品种和人员安全的处理方法</li>
<li><strong>症状稳定：</strong>在等待专业救治期间的症状稳定措施</li>
{f'<li><strong>中毒注意：</strong>不要自行催吐或给药，等待专业指导</li>' if is_emergency_poison else ''}
</ul>

<h3>⏰ 时间紧迫程度判断</h3>
<ul>
{f'<li><strong>🔴 中毒红色警报：</strong>立即就医，中毒情况每分钟都很关键</li>' if is_emergency_poison else ''}
<li><strong>立即就医（红色警报）：</strong>需要立即前往急诊的症状特征</li>
<li><strong>尽快就医（橙色警报）：</strong>24小时内需要就医的情况</li>
<li><strong>观察监护（黄色警报）：</strong>可以先行观察但需密切监护的情况</li>
<li><strong>{breed}品种特殊提醒：</strong>该品种需要特别注意的时间节点</li>
</ul>

<h3>📞 专业医疗联系</h3>
<ul>
{f'<li><strong>🆘 中毒急救热线：</strong>立即拨打宠物中毒控制中心或动物急救热线</li>' if is_emergency_poison else ''}
<li><strong>24小时急诊：</strong>寻找有{breed}品种经验的紧急宠物医院</li>
<li><strong>品种专科：</strong>联系熟悉{breed}品种的兽医专家</li>
<li><strong>电话咨询：</strong>在前往医院途中可联系的专业热线</li>
<li><strong>运输准备：</strong>适合{breed}品种的安全运输方式</li>
{f'<li><strong>携带证据：</strong>带上误食物质的包装、剩余物质或呕吐物样本</li>' if is_emergency_poison else ''}
</ul>

<h3>📝 症状记录与观察</h3>
<ul>
<li><strong>症状变化：</strong>需要重点观察和记录的症状变化</li>
<li><strong>时间记录：</strong>症状发生和变化的准确时间记录</li>
<li><strong>环境因素：</strong>可能影响{breed}品种的环境因素</li>
<li><strong>给医生信息：</strong>就医时需要向医生提供的关键信息</li>
{f'<li><strong>中毒详情：</strong>详细记录误食时间、物质类型、估计数量等</li>' if is_emergency_poison else ''}
</ul>

<div class="alert alert-danger">
<strong>⚠️ 最重要提醒：</strong>
<ul>
{f'<li><strong>中毒紧急情况：</strong>这是可能的中毒急救情况，请立即联系专业兽医，不要依赖在线咨询！</li>' if is_emergency_poison else ''}
<li>任何严重症状都应立即联系专业兽医，不要延误！</li>
<li>{breed}品种有其特殊的生理特点，紧急情况下更需要专业判断</li>
<li>本指导仅供参考，不能替代专业医疗诊断和治疗</li>
<li>如症状持续恶化或出现新症状，请立即前往最近的宠物急诊中心</li>
</ul>
</div>""",

        'general': f"""作为宠物综合护理专家，请为以下{breed}品种宠物提供全面的护理建议：
{base_info}
{breed_emphasis}

⚠️ 重要：请严格按照HTML格式输出，不要使用markdown语法！

请按以下HTML模板输出：

<h3>🏠 {breed}品种日常护理</h3>
<p>为{breed}品种制定的专属日常护理计划：</p>
<ul>
<li><strong>饮食管理：</strong>基于{breed}品种营养需求的饮食方案</li>
<li><strong>清洁护理：</strong>{breed}品种的特殊清洁和美容需求</li>
<li><strong>环境维护：</strong>适合{breed}品种的理想生活环境</li>
</ul>

<h3>💚 {breed}品种健康管理</h3>
<ul>
<li><strong>品种疾病预防：</strong>{breed}品种的遗传性疾病预防措施</li>
<li><strong>运动锻炼：</strong>基于{breed}品种活动需求的运动计划</li>
<li><strong>定期检查：</strong>{breed}品种建议的专项健康检查</li>
</ul>

<h3>🎓 {breed}品种行为训练</h3>
<ul>
<li><strong>基础训练：</strong>适合{breed}品种性格特点的训练方法</li>
<li><strong>社交化：</strong>{breed}品种的社会化训练重点</li>
<li><strong>问题行为：</strong>{breed}品种常见行为问题的解决方案</li>
</ul>

<h3>🏡 {breed}品种环境布置</h3>
<ul>
<li><strong>安全环境：</strong>针对{breed}品种特点的安全隐患排除</li>
<li><strong>舒适空间：</strong>基于{breed}品种体型和习性的空间设计</li>
<li><strong>娱乐设施：</strong>适合{breed}品种智力水平的玩具和设施</li>
</ul>

<h3>🔍 {breed}品种定期检查</h3>
<ul>
<li><strong>品种健康指标：</strong>{breed}品种需要特别监测的指标</li>
<li><strong>体检计划：</strong>基于{breed}品种特性的体检频率和项目</li>
<li><strong>疫苗接种：</strong>{breed}品种的个性化疫苗时间表</li>
</ul>

<div class="alert alert-info">
<strong>综合提示：</strong>{breed}品种有其独特的护理需求，请根据该品种的具体特性调整护理方案，建议咨询专业的{breed}品种饲养专家或兽医。
</div>"""
    }
    
    return prompts.get(consult_type, prompts['general'])


@login_required
def consultation_history_view(request):
    """咨询历史记录视图"""
    history_list = ConsultationHistory.objects.filter(user=request.user)
    
    # 搜索功能
    query = request.GET.get('q')
    if query:
        history_list = history_list.filter(
            models.Q(breed__icontains=query) |
            models.Q(pet_type__icontains=query) |
            models.Q(specific_question__icontains=query) |
            models.Q(advice__icontains=query)
        )
    
    # 类型筛选
    consult_type = request.GET.get('type')
    if consult_type:
        history_list = history_list.filter(consult_type=consult_type)
    
    paginator = Paginator(history_list, 5)  # 每页5条
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'consultations/consultation_history.html', {
        'page_obj': page_obj
    })


@login_required
def delete_consultation_history(request, pk):
    """删除咨询历史记录"""
    record = get_object_or_404(ConsultationHistory, pk=pk, user=request.user)
    record.delete()
    messages.success(request, '记录已成功删除')
    return redirect('consultations:consultation_history')
