# 🐾 智能宠物管理系统 (Pet Management System)

## 📋 项目概述

智能宠物管理系统是一个基于 **Django + DeepSeek AI** 的专业宠物健康管理平台，为宠物主人提供全方位的AI智能咨询、健康监控、详细记录管理和数据可视化分析服务。


## 🚀 项目架构

```
pet_management_yxk/                 # 项目根目录
├── 📁 项目文档
│   ├── README.md                    # 项目主文档 (本文件)
│   ├── README.en.md                 # 英文文档
│   ├── CHANGELOG.md                 # 版本更新日志
├── 📁 配置文件
│   ├── requirements.txt             # Python依赖包清单
│   ├── .env.example                 # 环境变量模板
│   ├── .gitignore                   # Git忽略配置
│   └── start_server_simple.bat     # 一键启动脚本
└── 📁 Django应用 (pet_site/)
    ├── manage.py                    # Django管理入口
    ├── db.sqlite3                   # SQLite数据库
    ├── 🔧 config/                   # 项目配置中心
    │   ├── settings.py              # 主配置文件
    │   ├── urls.py                  # 主URL路由
    │   ├── wsgi.py & asgi.py        # 服务器配置
    │   └── README.md                # 配置说明文档
    ├── 🏠 core/                     # 核心共享模块
    │   ├── models.py                # 基础模型和常量
    │   ├── views.py                 # 核心视图 (首页等)
    │   └── README.md                # 核心模块文档
    ├── 👤 accounts/                 # 用户管理系统
    │   ├── models.py                # 自定义用户模型
    │   ├── views.py                 # 用户认证视图
    │   ├── forms.py                 # 用户表单
    │   ├── templates/accounts/      # 用户界面模板
    │   ├── templatetags/            # 自定义模板标签
    │   └── README.md                # 用户系统文档
    ├── 🐾 pets/                     # 宠物档案管理
    │   ├── models.py                # 宠物数据模型
    │   ├── views.py                 # 宠物管理视图
    │   ├── forms.py                 # 宠物表单
    │   ├── admin.py                 # 后台管理配置
    │   ├── templates/pets/          # 宠物界面模板
    │   └── README.md                # 宠物模块文档
    ├── 🤖 consultations/            # AI咨询系统
    │   ├── models.py                # 咨询记录模型
    │   ├── views.py                 # AI咨询视图
    │   ├── forms.py                 # 咨询表单
    │   ├── templates/consultations/ # 咨询界面模板
    │   └── README.md                # 咨询系统文档
    ├── 📊 logs/                     # 智能日志系统
    │   ├── models.py                # 日志数据模型
    │   ├── views.py                 # 日志管理视图
    │   ├── ai_service.py            # AI分析服务
    │   ├── forms.py                 # 日志表单 
    │   ├── templates/logs/          # 日志界面模板
    │   │   ├── logs_center.html     # 日志管理中心
    │   │   ├── detailed_log_center.html # 详细记录管理中心
    │   │   ├── visualization_center.html # 数据可视化中心
    │   │   ├── feeding_log_form.html # 喂食记录表单
    │   │   ├── exercise_log_form.html # 运动记录表单
    │   │   ├── health_log_form.html  # 健康记录表单
    │   │   ├── medication_log_form.html # 用药记录表单
    │   │   └── ai_analysis_*.html    # AI分析相关页面
    │   ├── templatetags/            # 日志模板标签
    │   └── README.md                # 日志系统文档
    ├── 📁 templates/                # 全局模板
    │   └── base.html                # 基础模板框架
    ├── 📁 static/                   # 静态资源
    │   └── images/                  # 项目图片资源
    └── 📁 media/                    # 用户上传文件
        └── pets/                    # 宠物照片目录
```

## ✨ 核心功能模块

### 🤖 AI智能咨询系统
- **🎯 多维度分析**: 基于宠物品种、年龄、性别、绝育状态的个性化AI分析
- **🔍 专业咨询服务**: 涵盖日常饲养、疫苗接种、健康行为、紧急处理等全方位咨询
- **🛡️ 智能内容过滤**: 多层次安全检查，包括中毒关键词、伤害性内容、医疗误导等检测
- **📚 咨询历史管理**: 完整的咨询记录存储、查询和历史回顾功能
- **⚡ 实时AI响应**: 基于DeepSeek API的专业宠物健康建议和护理指导

### 📊 智能日志系统 (核心功能)

#### 🏠 日志管理中心
- **📈 统一数据面板**: 一站式日志管理和数据概览平台
- **📝 多维度记录**: 体重、食量、饮水量、心情、活跃度、体温等完整健康指标
- **🔔 智能提醒系统**: 基于历史数据分析的个性化护理提醒和异常预警
- **🗄️ 数据管理**: 每宠物最多300条记录，自动清理旧数据，保持系统性能

#### 📊 数据可视化中心
- **📈 交互式图表**: 动态数据可视化
- **🎛️ 时间范围筛选**: 支持7天、30天、90天等多种时间维度分析
- **🔄 实时更新**: 数据变更后图表自动刷新

#### 🗂️ 详细记录管理中心
- **🍽️ 喂食记录**: 食物类型、喂食时间、食量详细记录
- **🏃 运动记录**: 运动类型、时长、强度等级完整跟踪
- **🏥 健康记录**: 症状描述、严重程度、治疗方案管理
- **💊 用药记录**: 药物类型、剂量、用药时间、副作用完整记录
- **⚙️ CRUD操作**: 完整的增删改查功能，支持批量管理和数据导出

#### 🤖 AI智能分析
- **🧠 DeepSeek驱动**: 基于AI的宠物健康状态智能分析
- **📋 多类型分析**: 生长发育、健康状况、行为模式、营养评估、护理建议
- **📊 数据驱动**: 基于历史记录的趋势分析和预测
- **💡 个性化建议**: 针对每只宠物的专属护理建议

### 🐾 宠物档案管理
- **📋 完整档案系统**: 详细的宠物信息管理和品种数据库
- **📸 照片管理**: 宠物照片上传、展示和管理功能
- **🏥 健康档案**: 疫苗记录、医疗备注和健康状态跟踪
- **🐕 多宠物支持**: 用户可管理多只宠物的完整档案信息
- **🔍 智能搜索**: 支持按品种、年龄、状态等多维度筛选

### 👤 用户管理系统
- **🔐 安全认证**: 完整的用户注册、登录、密码管理功能
- **👥 个人中心**: 用户信息管理和偏好设置
- **🔒 数据隔离**: 确保用户数据安全和隐私保护
- **📱 响应式界面**: 适配各种设备的用户界面

## 🚀 快速开始


### ⚡ 一键启动 (推荐)
```bash
# 1. 克隆项目
git clone -b yxk https://gitee.com/ywhitegoose/pet_-management.git
cd pet_management_yxk

# 2. 复制环境变量模板
copy .env.example .env
# 编辑 .env 文件，设置 DEEPSEEK_API_KEY

# 3. 一键启动服务
start_server_simple.bat
```

### 🔧 手动安装配置

#### 1️⃣ 环境准备
```bash
# 安装依赖
pip install -r requirements.txt
```

#### 2️⃣ 环境变量配置
```bash
# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件
# 设置 DEEPSEEK_API_KEY = "your-api-key-here"
```

#### 3️⃣ 数据库初始化
```bash
cd pet_site

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户 (可选)
python manage.py createsuperuser
```

#### 4️⃣ 启动服务
```bash
# 启动开发服务器
python manage.py runserver

# 访问应用
# 前端: http://127.0.0.1:8000
```


## 🔍 故障排查

### ❌ 常见问题及解决方案

**1. DeepSeek API连接失败**
```bash
# 检查API密钥配置
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('DEEPSEEK_API_KEY'))"

# 测试网络连接
ping api.deepseek.com
```

**2. 数据库迁移错误**
```bash
# 重置迁移文件
python manage.py migrate --fake-initial

# 强制重新迁移
python manage.py migrate --run-syncdb
```

**3. 静态文件无法加载**
```bash
# 收集静态文件
python manage.py collectstatic

# 检查静态文件配置
python manage.py findstatic admin/css/base.css
```

### 🔧 开发调试

#### 启用DEBUG模式
```python
# .env 文件
DEBUG=True
```

#### 查看日志
```bash
# Django日志
python manage.py runserver --verbosity=2

# 数据库查询日志
# 在settings.py中添加LOGGING配置
```

