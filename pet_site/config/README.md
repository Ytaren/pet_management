# ⚙️ Config - Django项目配置中心

## 📋 配置概述
`config` 目录是智能宠物管理系统的核心配置中心，负责整个项目的设置管理、URL路由分发、服务器配置和环境变量管理。系统采用模块化架构设计，支持开发和生产环境的灵活切换，深度集成DeepSeek AI服务，提供完整的安全配置和性能优化。


## 🏗️ 配置架构
```
config/
├── __init__.py              # Python包标识
├── README.md               # 配置说明文档 (本文件)
├── settings.py             # Django主配置文件
├── urls.py                 # 主URL路由配置
├── wsgi.py                 # WSGI服务器配置
└── asgi.py                 # ASGI异步服务器配置
```

## 🗂️ 核心配置文件详解

### ⚙️ settings.py - 主配置文件
**功能**: Django项目的核心配置，包含所有系统设置

**关键配置项**:
- **应用注册**: 完整的INSTALLED_APPS配置
- **数据库设置**: SQLite3数据库配置
- **静态文件管理**: STATIC_URL、MEDIA_URL配置
- **模板引擎**: Django模板系统配置
- **中间件栈**: 安全和会话管理中间件
- **国际化设置**: 中文语言包和上海时区
- **用户认证**: 自定义用户模型和登录重定向
- **AI服务集成**: DeepSeek API密钥配置
- **环境变量支持**: dotenv环境变量管理

### 🌐 urls.py - URL路由配置
**功能**: 主URL路由分发器，将请求分发到各个应用

**路由结构**:
```python
urlpatterns = [
    path('admin/', admin.site.urls),           # Django后台管理
    path('', include('core.urls')),            # 核心页面路由
    path('accounts/', include('accounts.urls')), # 用户管理路由
    path('pets/', include('pets.urls')),       # 宠物管理路由
    path('consultations/', include('consultations.urls')), # AI咨询路由
    path('logs/', include('logs.urls')),       # 日志记录路由
]
```

### 🚀 wsgi.py - WSGI服务器配置
**功能**: Web服务器网关接口，用于生产环境部署

**特性**:
- 支持Apache、Nginx + uWSGI部署
- 生产环境优化配置
- 标准WSGI接口实现

### 🔄 asgi.py - ASGI异步服务器配置
**功能**: 异步服务器网关接口，支持异步功能

**特性**:
- WebSocket支持
- 异步任务处理
- Django Channels兼容

## 🏗️ 配置架构

## 🏗️ 应用架构配置

### 📱 INSTALLED_APPS 注册顺序
```python
INSTALLED_APPS = [
    # Django核心应用
    'django.contrib.admin',          # 后台管理系统
    'django.contrib.auth',           # 用户认证系统
    'django.contrib.contenttypes',   # 内容类型框架
    'django.contrib.sessions',       # 会话管理
    'django.contrib.messages',       # 消息框架
    'django.contrib.staticfiles',    # 静态文件管理
    
    # 自定义应用模块
    'core',                          # 核心共享模块
    'accounts',                      # 用户管理系统
    'pets',                          # 宠物档案管理
    'consultations',                 # AI咨询系统
    'logs',                          # 宠物日志记录
]
```

### 🔒 中间件配置栈
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',      # 安全中间件
    'django.contrib.sessions.middleware.SessionMiddleware', # 会话中间件
    'django.middleware.common.CommonMiddleware',          # 通用中间件
    'django.middleware.csrf.CsrfViewMiddleware',          # CSRF保护
    'django.contrib.auth.middleware.AuthenticationMiddleware', # 认证中间件
    'django.contrib.messages.middleware.MessageMiddleware',    # 消息中间件
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 点击劫持保护
]
```

### 📂 静态文件与媒体文件配置
```python
# 静态文件配置
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### URL路由结构
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('pets/', include('pets.urls')),
    path('consultations/', include('consultations.urls')),
    path('logs/', include('logs.urls')),
]
```


## 🌍 环境配置

### 开发环境特性
- DEBUG模式启用
- 详细错误信息
- 静态文件自动服务
- SQLite数据库

### 生产环境特性
- DEBUG模式关闭
- 安全头配置
- 数据库连接池
- 静态文件CDN



## 🚀 部署配置

### 环境变量
```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://...
DEEPSEEK_API_KEY=your-api-key
```

### 服务器配置
- Nginx配置示例
- Gunicorn配置
- 系统服务配置

## 🗄️ 数据库配置

### 💾 SQLite3 数据库设置
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**特性**:
- 🔧 **开发友好**: 无需额外安装数据库服务
- 📁 **文件存储**: 数据存储在项目根目录的db.sqlite3文件
- 🚀 **快速启动**: 零配置即可运行
- 📈 **扩展性**: 可轻松迁移到PostgreSQL/MySQL

## 🔐 安全与认证配置

### 👤 用户认证系统
```python
# 自定义用户模型
AUTH_USER_MODEL = 'accounts.CustomUser'

# 登录重定向配置
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'
```

### 🛡️ 密码验证规则
```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

## 🤖 AI服务配置

### 🧠 DeepSeek API集成
```python
# AI API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'default-key')
```

**功能支持**:
- 宠物健康分析
- 智能咨询服务
- 行为模式分析
- 营养建议生成

## 🔧 环境变量管理

### 📝 .env 文件配置
```env
# 安全密钥
SECRET_KEY=your-secret-key-here

# 调试模式
DEBUG=True

# 允许的主机
ALLOWED_HOSTS=localhost,127.0.0.1

# DeepSeek API密钥
DEEPSEEK_API_KEY=your-deepseek-api-key
```

### 🔄 环境变量加载
```python
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 使用环境变量
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')
```

## 🚀 部署配置

### 🔧 开发环境设置
```python
# 开发环境配置
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# 开发服务器启动
python manage.py runserver
```

### 🏭 生产环境配置
```python
# 生产环境配置
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# 静态文件收集
python manage.py collectstatic

# 数据库迁移
python manage.py migrate
```

### 🌐 WSGI部署示例
```python
# wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
```

## ⚙️ 高级配置

### 📊 日志配置
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 📧 邮件配置
```python
# 邮件后端配置（可选）
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

## 🌟 版本信息
**更新日期**: 2025年5月29日  


---

*📘 更多详细信息请参考Django官方文档和项目主README*
