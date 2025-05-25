# 🐾 智能宠物管理系统

## 📋 项目概述

智能宠物管理系统是一个基于Django + AI的Web应用，旨在为宠物主人提供专业的AI健康咨询服务。系统集成了DeepSeek AI大模型，能够根据不同宠物品种提供个性化的护理建议。

### 🏗️ 项目结构文件
```
pet_management_yxk/
├── README.md                    # 项目说明文档 ✅
├── README.en.md                 # 英文说明文档 ✅
├── requirements.txt             # Python依赖包 ✅
├── start_server.bat            # Windows批处理启动脚本 ✅
└── pet_site/                   # Django项目目录 ✅
    ├── manage.py               # Django管理脚本 ✅
    ├── db.sqlite3              # SQLite数据库文件 ✅
    ├── 注意事项.md             # 项目注意事项 ✅
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
    │   ├── utils.py           # 工具函数 ✅    
    │   ├── migrations/        # 数据库迁移文件 ✅
    │   │   ├── __init__.py
    │   │   ├── 0001_initial.py
    │   │   ├── 0002_consultationhistory.py
    │   │   ├── 0003_consultationhistory_consult_type_and_more.py
    │   │   ├── 0004_consultationhistory_emergency_symptoms.py
    │   │   └── 0005_consultationhistory_gender_and_more.py
    │   ├── templates/         # 模板文件 ✅
    │   │   └── accounts/
    │   │       ├── home.html
    │   │       ├── login.html
    │   │       ├── register.html
    │   │       ├── dashboard.html
    │   │       ├── pet_consult.html
    │   │       └── consultation_history.html
    │   └── templatetags/      # 自定义模板标签 ✅
    │       ├── __init__.py
    │       └── markdown_extras.py
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
- **个性化建议**：基于宠物年龄、体重、品种、性别、绝育状态的定制化方案
- **性别差异化护理**：针对雌性、雄性宠物的特殊护理需求
- **绝育状态考量**：考虑绝育/未绝育状态对健康管理的影响

### 👤 用户管理系统
- **安全认证**：用户注册、登录、个人中心
- **历史记录**：咨询历史查看、搜索、分页
- **个人数据**：安全的个人信息管理


## 🚀 快速开始

### 1️⃣ 克隆项目
```bash
# 克隆 yxk 分支
git clone -b yxk https://gitee.com/ywhitegoose/pet_-management.git

# 进入项目目录
cd pet_-management
```

### 2️⃣ 安装依赖
```bash
pip install -r requirements.txt
```

### 3️⃣ 配置环境变量
```powershell
# Windows PowerShell 复制环境变量模板
Copy-Item .env.example .env

# 或使用 CMD 命令
copy .env.example .env

# 编辑 .env 文件，配置您的 DeepSeek API 密钥
# 获取API密钥: https://platform.deepseek.com/
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

**方式一：使用启动脚本（推荐）**
```bash
# 返回项目根目录
cd ..

# Windows 批处理脚本启动
start_server.bat
```

**方式二：手动启动**
```bash
# 在 pet_site 目录下
python manage.py runserver

# 访问 http://127.0.0.1:8000
```

### 🔍 环境验证
```bash
# 检查Django项目配置
cd pet_site
python manage.py check

# 验证数据库连接
python manage.py showmigrations

# 测试环境变量加载
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key loaded:', bool(os.getenv('DEEPSEEK_API_KEY')))"
```

### ⚠️ 常见问题排查

**1. 环境变量未加载**
- 确保项目根目录存在 `.env` 文件
- 检查 `.env` 文件中的 `DEEPSEEK_API_KEY` 配置

**2. 依赖包安装失败**
```bash
# 升级pip
python -m pip install --upgrade pip

# 清除缓存重新安装
pip install -r requirements.txt --no-cache-dir
```

**3. 数据库迁移错误**
```bash
# 重置迁移
python manage.py migrate --fake-initial
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
3. **填写宠物信息**：详细填写宠物品种、年龄、体重、性别、绝育状态等信息
4. **智能表单交互**：性别选择将自动显示/隐藏绝育状态选项
5. **获取AI建议**：提交表单获得专业的AI分析建议
6. **查看历史记录**：管理和回顾历史咨询记录，包含完整的宠物信息

## 🌐 部署建议

```bash
python manage.py runserver
```



## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📝 更新日志

查看完整的版本更新记录请参考：[CHANGELOG.md](./CHANGELOG.md)

### 最新版本亮点 (v1.2.0)
- ✨ **性别信息管理**：支持雌性/雄性/未知三种性别选项
- ✨ **绝育状态追踪**：记录宠物的绝育状态（已绝育/未绝育/不确定）
- 🎨 **智能表单交互**：根据性别选择自动显示/隐藏绝育状态字段
- 🎯 **AI咨询增强**：考虑性别和绝育状态因素提供更精准的建议

---
