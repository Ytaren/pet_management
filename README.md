# 🐾 智能宠物管理系统

## 📋 项目概述

智能宠物管理系统是一个基于Django + AI的Web应用，旨在为宠物主人提供专业的AI健康咨询服务。系统集成了DeepSeek AI大模型，能够根据不同宠物品种提供个性化的护理建议。

### 🏗️ 项目结构 
```
pet_management_yxk/
├── README.md                    # 项目说明文档
├── README.en.md                 # 英文说明文档
├── .env.example                 # 环境变量模板
├── .gitignore                   # Git忽略配置
├── requirements.txt             # Python依赖包
├── start_server.bat            # Windows批处理启动脚本
└── pet_site/                   # Django项目目录
    ├── manage.py               # Django管理脚本
    ├── db.sqlite3              # SQLite数据库文件
    ├── config/                 # 项目配置
    │   ├── __init__.py
    │   ├── settings.py         # 项目设置
    │   ├── urls.py            # 主URL配置
    │   ├── wsgi.py            # WSGI配置
    │   └── asgi.py            # ASGI配置
    ├── core/                  # 核心共享模块
    │   ├── __init__.py
    │   ├── README.md          # 模块说明文档
    │   └── models.py          # 抽象模型和常量
    ├── accounts/              # 用户管理应用
    │   ├── __init__.py
    │   ├── README.md          # 应用说明文档
    │   ├── admin.py           # 管理后台配置
    │   ├── apps.py            # 应用配置
    │   ├── forms.py           # 用户表单
    │   ├── models.py          # 用户数据模型
    │   ├── views.py           # 用户视图逻辑
    │   ├── urls.py            # 用户URL路由
    │   ├── utils.py           # 用户工具函数
    │   ├── migrations/        # 数据库迁移文件
    │   ├── management/        # 自定义管理命令
    │   ├── templates/         # 用户模板文件
    │   │   └── accounts/
    │   │       ├── home.html          # 首页
    │   │       ├── login.html         # 登录页面
    │   │       ├── register.html      # 注册页面
    │   │       └── dashboard.html     # 用户仪表板
    │   └── templatetags/      # 自定义模板标签
    ├── pets/                  # 宠物档案管理应用
    │   ├── __init__.py
    │   ├── README.md          # 应用说明文档
    │   ├── admin.py           # 宠物管理后台
    │   ├── apps.py            # 应用配置
    │   ├── forms.py           # 宠物表单(已移除芯片功能)
    │   ├── models.py          # 宠物数据模型
    │   ├── views.py           # 宠物视图逻辑
    │   ├── urls.py            # 宠物URL路由
    │   ├── migrations/        # 数据库迁移文件
    │   ├── management/        # 自定义管理命令
    │   └── templates/         # 宠物模板文件
    │       └── pets/
    │           ├── pet_list.html      # 宠物列表
    │           ├── pet_detail.html    # 宠物详情
    │           └── pet_form.html      # 宠物表单
    ├── consultations/         # AI咨询系统应用
    │   ├── __init__.py
    │   ├── README.md          # 应用说明文档
    │   ├── admin.py           # 咨询管理后台
    │   ├── apps.py            # 应用配置
    │   ├── models.py          # 咨询相关模型
    │   ├── views.py           # 咨询视图逻辑
    │   ├── forms.py           # 咨询表单
    │   ├── urls.py            # 咨询URL路由
    │   ├── migrations/        # 数据库迁移文件
    │   └── templates/         # 咨询模板文件
    │       └── consultations/
    │           ├── pet_consult.html         # 宠物咨询表单
    │           └── consultation_history.html # 咨询历史记录
    ├── logs/                  # 宠物日志记录应用
    │   ├── __init__.py
    │   ├── README.md          # 应用说明文档
    │   └── (其他模块文件)
    ├── templates/             # 全局基础模板
    │   └── base.html          # 基础模板
    ├── static/                # 静态文件
    │   └── images/
    │       └── home-bg.jpg    # 首页背景图
    └── media/                 # 用户上传文件
        └── (宠物照片等)
```

## ✨ 核心功能

### 🤖 AI智能咨询系统 (独立模块)
- **品种差异化分析**：针对不同宠物品种提供专业建议
- **多类型咨询**：饲养、疫苗、健康、紧急症状等全方位咨询
- **个性化建议**：基于宠物年龄、体重、品种、性别、绝育状态的定制化方案
- **性别差异化护理**：针对雌性、雄性宠物的特殊护理需求
- **绝育状态考量**：考虑绝育/未绝育状态对健康管理的影响
- **安全内容检测**：内置恶意内容过滤和数据验证系统

### 👤 用户管理系统 
- **安全认证**：用户注册、登录、个人中心
- **权限控制**：基于Django的用户权限管理
- **用户仪表板**：功能导航和快捷入口
- **个人数据**：安全的个人信息管理

### 🐾 宠物档案管理
- **宠物档案**：完整的宠物信息管理
- **详细信息**：包含个性描述和医疗备注
- **品种数据库**：维护宠物品种信息
- **照片管理**：宠物照片上传和展示
- **体重记录**：宠物体重监控

### 📊 宠物日志系统
- **日常记录**：体重、饮食、运动等数据记录
- **健康监控**：健康状况变化追踪
- **数据分析**：趋势预测和异常提醒
- **智能报告**：基于历史数据的健康分析

### 🔧 核心共享模块
- **抽象模型**：为所有应用提供基础模型类
- **通用工具**：共享的工具函数和验证器
- **常量管理**：项目级别的选择常量定义
- **异常处理**：统一的错误处理机制

## 🛠️ 手动安装（高级用户）

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




## 📝 版本信息

### 最新版本亮点
- ✨ **宠物日志功能**：开发了宠物日志功能
- 🎯 **页面交互逻辑**：优化了页面交互逻辑


## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📞 支持与联系

如果您在使用过程中遇到问题或有改进建议，请：
- 提交 Issue 到项目仓库
- 查看相关应用的 README 文档
- 运行 `python manage.py check` 进行项目检查

---

