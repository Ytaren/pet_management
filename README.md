# 🐾 智能宠物管理系统

## 📋 项目概述

智能宠物管理系统是一个基于Django + AI的Web应用，旨在为宠物主人提供专业的AI健康咨询服务。系统集成了DeepSeek AI大模型，能够根据不同宠物品种提供个性化的护理建议。

### 🏗️ 项目结构文件
```
pet_-management-master/
├── README.md                    # 项目说明文档 ✅
├── requirements.txt             # Python依赖包 ✅
├── .gitignore                  # Git忽略规则 ✅
├── start_server.bat            # Windows批处理启动脚本 ✅
├── start_server.ps1            # PowerShell启动脚本 ✅
├── start_server.sh             # Linux/macOS启动脚本 ✅
├── STARTUP_GUIDE.md            # 启动指南 ✅
├── PROJECT_COMPLETION_REPORT.md # 项目完成报告 ✅
└── pet_site/                   # Django项目目录 ✅
    ├── manage.py               # Django管理脚本 ✅
    ├── config/                 # 项目配置 ✅
    │   ├── __init__.py
    │   ├── settings.py         # 项目设置 ✅
    │   ├── urls.py            # URL配置 ✅
    │   ├── wsgi.py            # WSGI配置 ✅
    │   └── asgi.py            # ASGI配置 ✅
    ├── accounts/              # 用户账户应用 ✅
    │   ├── __init__.py
    │   ├── admin.py           # 管理后台 ✅
    │   ├── apps.py            # 应用配置 ✅
    │   ├── forms.py           # 表单定义 ✅
    │   ├── models.py          # 数据模型 ✅
    │   ├── views.py           # 视图逻辑 ✅
    │   ├── urls.py            # URL路由 ✅
    │   ├── migrations/        # 数据库迁移文件 ✅
    │   │   ├── __init__.py
    │   │   ├── 0001_initial.py
    │   │   ├── 0002_consultationhistory.py
    │   │   ├── 0003_consultationhistory_consult_type_and_more.py
    │   │   └── 0004_consultationhistory_emergency_symptoms.py
    │   └── templates/         # 模板文件 ✅
    │       └── accounts/
    │           ├── home.html
    │           ├── login.html
    │           ├── register.html
    │           ├── dashboard.html
    │           ├── pet_consult.html
    │           └── consultation_history.html
    ├── templates/             # 基础模板 ✅
    │   └── base.html
    └── static/               # 静态文件 ✅
        └── images/
            └── home-bg.jpg
```

## ✨ 核心功能

### 🤖 AI智能咨询
- **品种差异化分析**：针对不同宠物品种提供专业建议
- **多类型咨询**：饲养、疫苗、健康、紧急症状等全方位咨询
- **个性化建议**：基于宠物年龄、体重、品种的定制化方案

### 👤 用户管理系统
- **安全认证**：用户注册、登录、个人中心
- **历史记录**：咨询历史查看、搜索、分页
- **个人数据**：安全的个人信息管理


## 🚀 快速开始

### 1️⃣ 克隆项目

### 2️⃣ 安装依赖
```bash
pip install -r requirements.txt
```

### 3️⃣ 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，配置您的API密钥
# DEEPSEEK_API_KEY=sk-your-actual-api-key-here
```

### 4️⃣ 数据库迁移
```bash
cd pet_site
python manage.py migrate
```

### 5️⃣ 创建超级用户（可选）
```bash
python manage.py createsuperuser
```

### 6️⃣ 启动服务
```bash
# Windows
../start_server.bat

# Linux/macOS
../start_server.sh

# 或手动启动
python manage.py runserver
```



## 🔧 功能模块

### 🍽️ 日常饲养建议
- 食物类型推荐
- 喂食量计算
- 喂食频率建议
- 饮水管理

### 💉 疫苗接种建议
- 疫苗类型选择
- 接种时间表
- 品种特异性建议
- 副作用监控

### 🏥 健康与行为管理
- 疾病预防
- 运动量建议
- 清洁护理
- 行为问题分析

### 🚨 紧急情况处理
- 症状快速评估
- 紧急程度判断
- 就医指导
- 应急处理建议

## 📱 使用指南

1. **注册账户**：创建个人账户，确保数据安全
2. **选择咨询类型**：根据需求选择相应的咨询类别
3. **填写宠物信息**：详细填写宠物品种、年龄、体重等信息
4. **获取AI建议**：提交表单获得专业的AI分析建议
5. **查看历史记录**：管理和回顾历史咨询记录

## 🌐 部署建议

### 开发环境
```bash
python manage.py runserver
```



## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request


---
