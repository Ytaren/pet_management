from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .forms import LoginForm, RegisterForm

import requests
import re
from django.conf import settings
from .forms import PetConsultForm

def home_view(request):
    return render(request, 'accounts/home.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, '登录成功！')
                return redirect('dashboard')
            else:
                messages.error(request, '用户名或密码错误')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, '您已成功退出登录')
    return redirect('home')

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')


'''
def pet_consult_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    advice = None
    if request.method == 'POST':
        form = PetConsultForm(request.POST)
        if form.is_valid():
            # 准备DeepSeek API请求
            prompt = f"""作为专业兽医，请根据以下信息提供喂养方案：
宠物种类：{form.cleaned_data['pet_type']}
品种：{form.cleaned_data['breed']}
年龄：{form.cleaned_data['age']}岁
体重：{form.cleaned_data['weight']}kg

请给出：
1. 每日饮食建议（分幼年/成年/老年）
2. 运动建议
3. 健康注意事项
4. 常见疾病预防"""

            # 调用DeepSeek API（示例）
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
                }
            )
            
            if response.status_code == 200:
                advice = response.json()['choices'][0]['message']['content']
            else:
                advice = "API请求失败，请稍后再试"
    else:
        form = PetConsultForm()

    return render(request, 'accounts/pet_consult.html', {
        'form': form,
        'advice': advice
    })

# 修改咨询视图保存记录
from .models import ConsultationHistory

def pet_consult_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = PetConsultForm(request.POST)
        if form.is_valid():
            # ...原有API调用代码...
            
            if response.status_code == 200:
                advice = response.json()['choices'][0]['message']['content']
                # 保存记录
                ConsultationHistory.objects.create(
                    user=request.user,
                    pet_type=form.cleaned_data['pet_type'],
                    breed=form.cleaned_data['breed'],
                    age=form.cleaned_data['age'],
                    weight=form.cleaned_data['weight'],
                    advice=advice
                )
            else:
                advice = "API请求失败，请稍后再试"
'''

# 视图
import requests
import re
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import PetConsultForm
from .models import ConsultationHistory

def validate_pet_data(pet_type, age, weight, specific_question, emergency_symptoms):
    """
    宠物数据安全验证函数
    检查数据逻辑合理性和恶意内容
    """
    
    # 🔍 数据逻辑验证
    logical_checks = {
        '猫': {'age_max': 25, 'weight_min': 0.5, 'weight_max': 15},
        '狗': {'age_max': 25, 'weight_min': 0.5, 'weight_max': 100},
        '兔子': {'age_max': 15, 'weight_min': 0.3, 'weight_max': 8},
        '鸟': {'age_max': 100, 'weight_min': 0.01, 'weight_max': 5},
        '鱼': {'age_max': 30, 'weight_min': 0.001, 'weight_max': 50},
        '其他': {'age_max': 100, 'weight_min': 0.001, 'weight_max': 200}  # 宽松限制
    }
    
    # 年龄验证
    try:
        age_num = float(age)
        if age_num < 0:
            return {'is_valid': False, 'error_message': '年龄不能为负数'}
        if age_num > 150:  # 任何宠物都不可能超过150岁
            return {'is_valid': False, 'error_message': '年龄数据异常，请检查是否为宠物真实年龄'}
            
        # 根据宠物类型验证年龄
        pet_limits = logical_checks.get(pet_type, logical_checks['其他'])
        if age_num > pet_limits['age_max']:
            return {'is_valid': False, 'error_message': f'{pet_type}的年龄通常不超过{pet_limits["age_max"]}岁，请核实信息'}
    except (ValueError, TypeError):
        return {'is_valid': False, 'error_message': '年龄格式错误，请输入有效数字'}
    
    # 体重验证
    try:
        weight_num = float(weight)
        if weight_num <= 0:
            return {'is_valid': False, 'error_message': '体重必须大于0'}
        if weight_num > 1000:  # 超过1000kg明显异常
            return {'is_valid': False, 'error_message': '体重数据异常，请检查是否为宠物真实体重'}
            
        # 根据宠物类型验证体重
        pet_limits = logical_checks.get(pet_type, logical_checks['其他'])
        if weight_num < pet_limits['weight_min'] or weight_num > pet_limits['weight_max']:
            return {'is_valid': False, 'error_message': f'{pet_type}的体重通常在{pet_limits["weight_min"]}-{pet_limits["weight_max"]}kg范围内，请核实信息'}
    except (ValueError, TypeError):
        return {'is_valid': False, 'error_message': '体重格式错误，请输入有效数字'}
      # 🚨 恶意内容检测
    malicious_keywords = [
        # 暴力伤害类
        '杀死', '杀害', '弄死', '毒死', '毒害', '虐待', '虐杀', '折磨', '伤害',
        '打死', '踢死', '摔死', '掐死', '闷死', '饿死', '冻死', '烫死',
        '割', '切', '砍', '刺', '烧', '烫', '电击', '殴打', '踢打', '窒息',
        
        # 遗弃类
        '扔掉', '丢掉', '抛弃', '不要了', '处理掉', '解决掉', '遗弃', '抛弃',
        
        # 危险药物和化学品类（包含误服情况的专业术语）
        '人用药', '毒药', '老鼠药', '杀虫剂', '农药', '漂白剂', '除草剂',
        '消毒液', '洗洁精', '洗衣液', '酒精', '双氧水', '碘酒', '红药水',
        '安眠药', '抗抑郁药', '降压药', '胰岛素', '阿司匹林', '扑热息痛',
        '感冒药', '止痛药', '抗生素', '维生素过量', '巧克力中毒',
        '洋葱中毒', '葡萄中毒', '木糖醇', '咖啡因', '尼古丁',
        '清洁剂', '杀蟑螂药', '蚊香', '樟脑丸', '防冻剂', '汽油', '煤油',
        
        # 色情和不当内容类
        '性交', '交配', '配种', '发情', '生殖器', '阴茎', '阴道', '肛门',
        '性器官', '性行为', '手淫', '自慰', '性虐', '性侵', '强奸',
        '裸体', '色情', '淫秽', '猥亵', '露体', '性感', '诱惑',
        '做爱', '性爱', '激情', '床戏', 'sex', 'porn', 'sexy', 'nude',
        
        # 其他危险行为
        '实验', '解剖', '卖掉', '吃掉', '煮', '炖', '烤', '屠宰',
        '买卖', '贩卖', '交易', '赌博', '斗宠', '斗狗', '斗鸡',
        '繁殖场', '宠物繁殖', '配种赚钱', '生育机器',
        
        # 迷信和伪科学类
        '做法', '巫术', '诅咒', '风水', '转运', '辟邪', '招财',
        
        # 英文恶意词汇
        'kill', 'murder', 'abuse', 'torture', 'harm', 'poison', 'abandon',
        'sex', 'porn', 'naked', 'nude', 'sexual', 'rape', 'drug', 'cocaine',
        'heroin', 'cannabis', 'marijuana', 'alcohol', 'suicide', 'death'    ]
    
    # 检查具体问题和紧急症状中的恶意内容
    text_to_check = f"{specific_question} {emergency_symptoms}".lower()
    
    # 分类检测不同类型的违规内容，提供针对性提示
    
    # 1. 药物中毒紧急情况检测
    emergency_drug_keywords = [
        '误食', '误服', '中毒', '吃了', '喝了', '舔了', '咬了',
        '农药', '老鼠药', '杀虫剂', '漂白剂', '消毒液', '洗洁精', 
        '巧克力', '洋葱', '葡萄', '木糖醇', '咖啡', '酒精'
    ]
    
    for keyword in emergency_drug_keywords:
        if keyword in text_to_check:
            # 这是紧急中毒情况，需要特殊处理
            return {
                'is_valid': True,  # 允许通过，但会在AI回复中特别标注
                'error_message': '',
                'is_emergency_poison': True  # 新增标志
            }
    
    # 2. 危险药物和化学品检测（非紧急咨询）
    dangerous_substances = [
        '人用药', '毒药', '安眠药', '抗抑郁药', '降压药', '胰岛素',
        '阿司匹林', '扑热息痛', '感冒药', '止痛药', '抗生素',
        '清洁剂', '杀蟑螂药', '蚊香', '樟脑丸', '防冻剂', '汽油', '煤油'    ]
    
    for keyword in dangerous_substances:
        if keyword in text_to_check:
            return {
                'is_valid': False,
                'error_message': '⚠️ 检测到危险药物相关内容。<br><br>🚨 如果是中毒紧急情况：<br>• 立即联系宠物医院急诊<br>• 拨打动物中毒控制热线<br><br>💊 关于药物咨询请找专业兽医。'
            }
    
    # 3. 色情和不当内容检测
    inappropriate_content = [
        '性交', '交配', '生殖器', '阴茎', '阴道', '性器官', 
        '性行为', '手淫', '自慰', '性虐', '性侵', '强奸', '裸体', 
        '色情', '淫秽', '猥亵', '露体', '性感', '诱惑', '做爱', 
        '性爱', '激情', 'sex', 'porn', 'sexy', 'nude', 'sexual', 'rape'    ]
    
    for keyword in inappropriate_content:
        if keyword in text_to_check:
            return {
                'is_valid': False,
                'error_message': '🚫 检测到不当内容。<br><br>本平台仅提供健康宠物护理咨询。<br><br>繁殖相关问题请咨询：<br>• 专业宠物繁殖医师<br>• 动物繁殖专家'
            }
    
    # 4. 暴力伤害内容检测
    violence_keywords = [
        '杀死', '杀害', '弄死', '毒死', '虐待', '虐杀', '折磨', '伤害',
        '打死', '踢死', '摔死', '掐死', '闷死', '饿死', '冻死', '烫死',
        '割', '切', '砍', '刺', '烧', '烫', '电击', '殴打', '踢打', '窒息'    ]
    
    for keyword in violence_keywords:
        if keyword in text_to_check:
            return {
                'is_valid': False,
                'error_message': '🛑 检测到暴力内容。<br><br>本平台严禁伤害动物的内容。<br><br>如遇虐待情况请联系：<br>• 当地动物保护组织<br>• 110报警求助'
            }
    
    # 5. 遗弃和非法交易检测
    abandon_trade_keywords = [
        '扔掉', '丢掉', '抛弃', '不要了', '处理掉', '解决掉', '遗弃',
        '卖掉', '买卖', '贩卖', '交易', '斗宠', '斗狗', '斗鸡'    ]
    
    for keyword in abandon_trade_keywords:
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
    
    return {'is_valid': True, 'error_message': ''}

def pet_consult_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    advice = None
    if request.method == 'POST':
        form = PetConsultForm(request.POST)
        if form.is_valid():
            response = None
            
            try:                # 根据咨询类型生成不同的提示词
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
                    advice = f"API请求失败，状态码：{response.status_code}。请检查您的API密钥配置。"                # 保存咨询记录
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

    return render(request, 'accounts/pet_consult.html', {
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
⚠️ 重要提醒：请务必针对{breed}品种的具体特性进行分析，同时考虑以下因素：
1. {breed}品种的遗传特点和常见健康问题
2. {breed}品种的性格特征和行为习性
3. {breed}品种的特殊营养需求和禁忌
4. {breed}品种的运动需求和训练特点
5. {breed}品种的护理重点和注意事项
6. 🔸 性别差异：{gender_display}宠物在{breed}品种中的特殊需求
7. 🔸 绝育影响：{neutered_display}状态对{breed}品种健康和行为的影响

请不要给出泛泛的{pet_type}类建议，而要基于{breed}品种、{gender_display}、{neutered_display}的具体特性提供专业指导。
"""
    
    prompts = {
        'feeding': f"""作为专业宠物营养师，请为以下{breed}品种宠物提供详细的日常饲养建议：
{base_info}
{breed_emphasis}

⚠️ 重要：请严格按照HTML格式输出，不要使用markdown语法！

请按以下HTML模板输出：

<h3>🍽️ {breed}品种专属食物推荐</h3>
<p>根据{breed}品种的特殊营养需求，推荐以下食物类型：</p>
<ul>
<li><strong>主粮选择：</strong>针对{breed}品种特性的专用粮食推荐</li>
<li><strong>营养补充：</strong>{breed}品种易缺乏的维生素、矿物质补充</li>
<li><strong>零食推荐：</strong>适合{breed}品种的健康零食选择</li>
<li><strong>品种禁忌：</strong>{breed}品种应避免的食物和成分</li>
</ul>

<h3>⚖️ {breed}品种专属喂食量建议</h3>
<p>针对体重{weight}kg，年龄{age}岁的{breed}品种：</p>
<ul>
<li><strong>每日总量：</strong>基于{breed}品种代谢特点的具体克数</li>
<li><strong>分餐安排：</strong>考虑{breed}品种消化特性的分餐方案</li>
<li><strong>体重管理：</strong>{breed}品种的理想体重范围和控制方法</li>
</ul>

<h3>⏰ {breed}品种喂食频率</h3>
<ul>
<li><strong>幼年期：</strong>针对{breed}品种幼犬/幼猫的喂食安排</li>
<li><strong>成年期：</strong>适合成年{breed}品种的最佳喂食频率</li>
<li><strong>老年期：</strong>老年{breed}品种的特殊饮食安排</li>
</ul>

<h3>💧 {breed}品种饮水指导</h3>
<ul>
<li><strong>每日需水量：</strong>基于{breed}品种活动量的水分需求</li>
<li><strong>饮水方式：</strong>适合{breed}品种特点的饮水方法</li>
<li><strong>水质要求：</strong>{breed}品种对水质的特殊要求</li>
</ul>

<div class="alert alert-info">
<strong>温馨提示：</strong>{breed}品种有其独特的饮食需求，请严格按照品种特性调整饮食方案，如有特殊需求请咨询专业兽医。
</div>""",

        'vaccine': f"""作为宠物疫苗接种专家，请为以下{breed}品种宠物提供疫苗接种建议：
{base_info}
{breed_emphasis}

⚠️ 重要：请严格按照HTML格式输出，不要使用markdown语法！

请按以下HTML模板输出：

<h3>💉 {breed}品种核心疫苗</h3>
<p>{breed}品种必须接种的核心疫苗，考虑该品种的遗传易感性：</p>
<ul>
<li><strong>品种特异性疫苗：</strong>针对{breed}品种高发疾病的疫苗</li>
<li><strong>常规核心疫苗：</strong>适合{breed}品种的标准疫苗方案</li>
</ul>

<h3>🔸 {breed}品种非核心疫苗</h3>
<p>根据{breed}品种的生活特点和易感疾病推荐的选择性疫苗：</p>
<ul>
<li><strong>品种推荐疫苗：</strong>基于{breed}品种特性的额外保护</li>
<li><strong>环境风险疫苗：</strong>结合{breed}品种活动特点的疫苗选择</li>
</ul>

<h3>📅 {breed}品种接种时间表</h3>
<p>根据年龄{age}岁，体重{weight}kg的{breed}品种特殊需求：</p>
<ul>
<li><strong>品种优化方案：</strong>考虑{breed}品种免疫发育特点的时间安排</li>
<li><strong>加强免疫：</strong>基于{breed}品种抗体衰减规律的加强计划</li>
</ul>

<h3>⚠️ {breed}品种特殊注意事项</h3>
<ul>
<li><strong>品种过敏风险：</strong>{breed}品种可能的疫苗过敏反应</li>
<li><strong>接种前准备：</strong>{breed}品种接种前的特殊检查</li>
<li><strong>接种后观察：</strong>{breed}品种需要特别关注的副作用</li>
</ul>

<h3>📋 {breed}品种后续计划</h3>
<ul>
<li><strong>个性化计划：</strong>基于{breed}品种特性的长期免疫方案</li>
<li><strong>健康监测：</strong>{breed}品种的疫苗效果评估方法</li>
</ul>

<div class="alert alert-warning">
<strong>重要提醒：</strong>{breed}品种有其特殊的免疫特点，建议咨询熟悉该品种的专业兽医确认具体疫苗方案。
</div>""",

        'health': f"""作为宠物健康与行为专家，请为以下{breed}品种宠物提供健康管理建议：
{base_info}
{breed_emphasis}

⚠️ 重要：请严格按照HTML格式输出，不要使用markdown语法！

请按以下HTML模板输出：

<h3>🛡️ {breed}品种疾病预防</h3>
<p>针对{breed}品种的遗传易感疾病和常见健康问题：</p>
<ul>
<li><strong>{breed}品种高发疾病：</strong>该品种特有的遗传性疾病预防</li>
<li><strong>品种易感问题：</strong>{breed}品种容易出现的健康问题及预防</li>
<li><strong>早期筛查：</strong>{breed}品种建议的定期检查项目</li>
</ul>

<h3>🏃 {breed}品种运动建议</h3>
<p>根据{breed}品种的体型特点、能量水平和年龄{age}岁，体重{weight}kg：</p>
<ul>
<li><strong>品种运动需求：</strong>基于{breed}品种天性的运动量和类型</li>
<li><strong>运动强度控制：</strong>适合{breed}品种的运动强度和时长</li>
<li><strong>品种特殊考虑：</strong>{breed}品种运动时需要特别注意的事项</li>
</ul>

<h3>🧼 {breed}品种清洁护理</h3>
<ul>
<li><strong>毛发护理：</strong>{breed}品种的毛质特点和专用护理方法</li>
<li><strong>皮肤护理：</strong>{breed}品种常见皮肤问题和护理重点</li>
<li><strong>五官护理：</strong>基于{breed}品种面部结构的清洁要点</li>
<li><strong>指甲修剪：</strong>{breed}品种的指甲生长特点和修剪技巧</li>
</ul>

<h3>🧠 {breed}品种行为管理</h3>
<ul>
<li><strong>性格特征：</strong>{breed}品种的典型性格和行为特点</li>
<li><strong>训练重点：</strong>基于{breed}品种智力和服从性的训练方法</li>
<li><strong>行为问题：</strong>{breed}品种常见的行为问题及纠正方法</li>
<li><strong>社交需求：</strong>{breed}品种的社交特点和环境适应</li>
</ul>

<h3>📊 {breed}品种健康监测</h3>
<ul>
<li><strong>品种指标：</strong>{breed}品种需要特别监测的健康指标</li>
<li><strong>检查频率：</strong>基于{breed}品种特性的体检建议</li>
<li><strong>异常信号：</strong>{breed}品种特有的疾病早期症状</li>
</ul>

<div class="alert alert-success">
<strong>健康提示：</strong>{breed}品种有其独特的健康特点，建议寻找熟悉该品种的专业兽医进行定期健康管理。
</div>""",        'emergency': f"""作为专业宠物急救医师，请基于以下{breed}品种宠物的紧急症状提供专业指导：
{base_info}
{breed_emphasis}

⚠️ 症状分析重点：请重点分析所描述的症状，结合{breed}品种特性、年龄{age}岁、体重{weight}kg的具体情况进行判断。

{"""
🚨 **特别提醒：检测到可能的宠物中毒紧急情况** 🚨

这可能是宠物误食有害物质的紧急情况。请立即：
1. 记录宠物误食的具体物质和数量（如能确定）
2. 立即联系宠物急救热线或最近的宠物医院
3. 不要自行催吐，除非医生明确指示
4. 保存误食物质的包装或样本带给医生
5. 立即前往宠物医院，在路上可电话咨询医生

⚠️ 时间就是生命，请不要在网上寻找解决方案，立即寻求专业医疗帮助！
""" if is_emergency_poison else ""}

⚠️ 重要：请严格按照HTML格式输出，不要使用markdown语法！

请按以下HTML模板输出：

<div class="alert alert-danger">
<h4>🚨 紧急评估结果</h4>
<p>基于描述的症状和{breed}品种特点的紧急程度评估</p>
{f'<p><strong>⚠️ 中毒警报：</strong>检测到宠物可能误食有害物质，这是医疗紧急情况，请立即联系兽医！</p>' if is_emergency_poison else ''}
</div>

<h3>🔍 症状分析与{breed}品种关联</h3>
<p>针对所描述症状的专业分析：</p>
<ul>
<li><strong>症状严重程度：</strong>基于{breed}品种特性评估症状的危险等级</li>
<li><strong>品种特异性风险：</strong>{breed}品种对这类症状的特殊易感性</li>
<li><strong>年龄体重因素：</strong>{age}岁、{weight}kg对症状严重程度的影响</li>
<li><strong>可能原因分析：</strong>结合{breed}品种常见疾病的可能病因</li>
{f'<li><strong>中毒风险评估：</strong>基于{breed}品种的代谢特点和{weight}kg体重评估中毒风险</li>' if is_emergency_poison else ''}
</ul>

<h3>🩹 立即处理措施</h3>
<p>针对当前症状的紧急处理步骤：</p>
<ul>
{f'<li><strong>🚨 中毒急救优先：</strong>立即联系中毒控制中心或宠物急诊，说明误食物质</li>' if is_emergency_poison else ''}
<li><strong>第一步：</strong>基于{breed}品种特点的安全固定和评估</li>
<li><strong>第二步：</strong>针对具体症状的应急处理方法</li>
<li><strong>第三步：</strong>考虑{breed}品种体型的搬运和运输准备</li>
<li><strong>注意事项：</strong>{breed}品种在紧急情况下的特殊注意点</li>
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

# 创建历史视图
from django.core.paginator import Paginator

def consultation_history_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
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
    
    return render(request, 'accounts/consultation_history.html', {
        'page_obj': page_obj    })

# 删除历史记录
@login_required
def delete_consultation_history(request, pk):
    record = get_object_or_404(ConsultationHistory, pk=pk, user=request.user)
    record.delete()
    messages.success(request, '记录已成功删除')
    return redirect('consultation_history')