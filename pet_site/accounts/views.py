from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .forms import LoginForm, RegisterForm

import requests
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
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import PetConsultForm
from .models import ConsultationHistory

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
    """根据咨询类型生成专业的AI提示词"""
    
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
</div>""",

        'emergency': f"""作为专业宠物急救医师，请基于以下{breed}品种宠物的紧急症状提供专业指导：
{base_info}
{breed_emphasis}

⚠️ 症状分析重点：请重点分析所描述的症状，结合{breed}品种特性、年龄{age}岁、体重{weight}kg的具体情况进行判断。

⚠️ 重要：请严格按照HTML格式输出，不要使用markdown语法！

请按以下HTML模板输出：

<div class="alert alert-danger">
<h4>🚨 紧急评估结果</h4>
<p>基于描述的症状和{breed}品种特点的紧急程度评估</p>
</div>

<h3>🔍 症状分析与{breed}品种关联</h3>
<p>针对所描述症状的专业分析：</p>
<ul>
<li><strong>症状严重程度：</strong>基于{breed}品种特性评估症状的危险等级</li>
<li><strong>品种特异性风险：</strong>{breed}品种对这类症状的特殊易感性</li>
<li><strong>年龄体重因素：</strong>{age}岁、{weight}kg对症状严重程度的影响</li>
<li><strong>可能原因分析：</strong>结合{breed}品种常见疾病的可能病因</li>
</ul>

<h3>🩹 立即处理措施</h3>
<p>针对当前症状的紧急处理步骤：</p>
<ul>
<li><strong>第一步：</strong>基于{breed}品种特点的安全固定和评估</li>
<li><strong>第二步：</strong>针对具体症状的应急处理方法</li>
<li><strong>第三步：</strong>考虑{breed}品种体型的搬运和运输准备</li>
<li><strong>注意事项：</strong>{breed}品种在紧急情况下的特殊注意点</li>
</ul>

<h3>⏰ 时间紧迫程度判断</h3>
<ul>
<li><strong>立即就医（红色警报）：</strong>需要立即前往急诊的症状特征</li>
<li><strong>尽快就医（橙色警报）：</strong>24小时内需要就医的情况</li>
<li><strong>观察监护（黄色警报）：</strong>可以先行观察但需密切监护的情况</li>
<li><strong>{breed}品种特殊提醒：</strong>该品种需要特别注意的时间节点</li>
</ul>

<h3>📞 专业医疗联系</h3>
<ul>
<li><strong>24小时急诊：</strong>寻找有{breed}品种经验的紧急宠物医院</li>
<li><strong>品种专科：</strong>联系熟悉{breed}品种的兽医专家</li>
<li><strong>电话咨询：</strong>在前往医院途中可联系的专业热线</li>
<li><strong>运输准备：</strong>适合{breed}品种的安全运输方式</li>
</ul>

<h3>📝 症状记录与观察</h3>
<ul>
<li><strong>症状变化：</strong>需要重点观察和记录的症状变化</li>
<li><strong>时间记录：</strong>症状发生和变化的准确时间记录</li>
<li><strong>环境因素：</strong>可能影响{breed}品种的环境因素</li>
<li><strong>给医生信息：</strong>就医时需要向医生提供的关键信息</li>
</ul>

<div class="alert alert-danger">
<strong>⚠️ 最重要提醒：</strong>
<ul>
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