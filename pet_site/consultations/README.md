# 🤖 Consultations 应用 - AI咨询系统

## 📋 应用概述
`consultations` 应用是独立的AI咨询系统，专门负责宠物智能咨询功能。该应用提供专业、安全、完整的宠物护理建议服务，集成DeepSeek AI大模型。

## 🏗️ 应用架构 (独立模块)
```
consultations/
├── __init__.py              # 应用初始化
├── README.md               # 应用说明文档 (本文件)
├── admin.py                # 后台管理配置
├── apps.py                 # 应用配置
├── models.py               # 咨询数据模型
├── views.py                # 咨询视图逻辑
├── forms.py                # 咨询表单
├── urls.py                 # URL路由配置 (使用consultations命名空间)
├── migrations/             # 数据库迁移文件
└── templates/              # 模板文件
    └── consultations/
        ├── pet_consult.html         # 咨询表单页面
        └── consultation_history.html # 咨询历史页面
```

## 🚀 应用特色
- **独立架构**: 从accounts应用迁移而来，实现模块化设计
- **AI集成**: 深度集成DeepSeek AI大模型
- **安全优先**: 多层次数据验证和内容过滤
- **用户体验**: 智能表单交互和历史记录管理

## 📄 核心文件说明

### 🗃️ 数据模型 (`models.py`)
- `ConsultationHistory` - 咨询历史记录模型
  - 用户关联、宠物信息、咨询类型
  - AI响应内容、创建时间
  - 安全的数据存储和查询
- `ConsultationHistoryManager` - 自定义模型管理器

### 🎯 视图逻辑 (`views.py`)
- `pet_consult_view` - AI咨询处理核心视图
- `consultation_history_view` - 咨询历史查看(支持搜索分页)
- `delete_consultation_history` - 删除咨询记录
- `validate_pet_data` - 数据安全验证函数
- `generate_prompt` - 智能提示词生成函数

### 📝 表单管理 (`forms.py`)
- `PetConsultForm` - 宠物咨询表单
  - 智能性别/绝育状态联动
  - 多种咨询类型支持
  - 数据验证和清理
- **紧急情况识别**：自动识别中毒等紧急情况

### 3. 📊 咨询历史管理
- **完整记录保存**：详细的咨询历史记录
- **搜索过滤功能**：支持关键词搜索和类型筛选
- **分页显示**：优化大量数据的显示性能

### 4. 📈 用户体验优化
- **响应式界面**：适配多种设备屏幕
- **实时反馈**：咨询状态和结果实时显示
- **错误处理**：友好的错误提示和处理

## 📊 咨询类型详解

### 🍽️ 饲养咨询 (feeding)
- 品种专属食物推荐
- 个性化喂食量计算
- 营养补充建议
- 饮水指导

### 💉 疫苗咨询 (vaccine)
- 品种特异性疫苗方案
- 个性化接种时间表
- 疫苗风险评估
- 接种后护理指导

### 🏃‍♂️ 健康咨询 (health)
- 疾病预防建议
- 运动方案制定
- 护理技巧指导
- 行为分析

### 🚨 紧急咨询 (emergency)
- 症状严重程度评估
- 应急处理措施
- 就医指导建议
- 中毒情况特殊处理

## 🔗 数据模型字段

### ConsultationHistory 模型
```python
# 基础信息
user = ForeignKey(User)                    # 关联用户
consult_type = CharField(max_length=20)    # 咨询类型
pet_type = CharField(max_length=50)        # 宠物类型
breed = CharField(max_length=100)          # 宠物品种
age = DecimalField(max_digits=4)           # 年龄
weight = DecimalField(max_digits=5)        # 体重

# 扩展信息
gender = CharField(max_length=10)          # 性别
is_neutered = CharField(max_length=10)     # 绝育状态
specific_question = TextField()            # 具体问题
emergency_symptoms = TextField()           # 紧急症状

# 回复和评价
advice = TextField()                       # AI建议内容
user_rating = IntegerField()               # 用户评分
confidence_score = FloatField()            # 置信度评分

# 时间戳
created_at = DateTimeField()               # 创建时间
updated_at = DateTimeField()               # 更新时间
```

## 🔗 关联关系
- 与 `accounts` 应用：多对一关系（多次咨询对应一个用户）
- 与 `core` 应用：使用共享的选择常量和工具函数
- 独立于其他业务模块，实现松耦合架构

## 🌐 URL 命名空间
```python
app_name = 'consultations'

urlpatterns = [
    path('pet-consult/', views.pet_consult_view, name='pet_consult'),
    path('history/', views.consultation_history_view, name='consultation_history'),
    path('delete/<int:pk>/', views.delete_consultation_history, name='delete_consultation_history'),
]
```

## 🔧 配置要求
- **Django**: ≥ 4.0
- **DeepSeek API**: 需要配置有效的API密钥
- **数据库**: 支持SQLite/PostgreSQL/MySQL
- **依赖包**: requests, django

## 🚀 使用示例
```python
# 在模板中使用
{% url 'consultations:pet_consult' %}?type=feeding
{% url 'consultations:consultation_history' %}

# 在视图中使用
from django.urls import reverse
redirect('consultations:pet_consult')
```

## 📈 性能优化
- 自动限制用户记录数量（默认150条）
- 分页查询优化大数据量显示
- 缓存常用查询结果
- 异步AI接口调用

## 🔒 安全特性
- 输入数据验证和清理
- 恶意内容检测和过滤
- 用户权限验证
- API调用频率限制

## 📝 维护说明
- 定期清理历史数据
- 监控AI接口调用状态
- 更新安全规则和验证逻辑
- 优化提示词模板

**最后更新**: 2025年5月25日
**维护者**: 开发团队
```
ConsultationType:
├── feeding (日常饲养建议)
├── vaccine (疫苗接种建议)
├── health (健康与行为建议)
├── emergency (紧急情况指引)
└── general (综合咨询)
```

## 🛡️ 安全机制
- **输入验证** - 数据格式和逻辑验证
- **内容过滤** - 恶意内容检测和阻止
- **分类提示** - 针对性的错误提示
- **审计日志** - 安全事件记录

## 🚀 未来扩展
- 多语言AI支持
- 语音咨询功能
- 图像识别诊断
- 专家医师接入
