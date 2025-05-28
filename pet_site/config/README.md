# ⚙️ Config - Django项目配置

## 📋 配置概述
`config` 目录包含Django项目的核心配置文件，负责整个项目的设置、URL路由和WSGI/ASGI配置。

## 🗂️ 文件结构说明

### 📄 核心配置文件
- **`settings.py`** - Django项目主配置文件
  - 数据库配置
  - 应用注册 (INSTALLED_APPS)
  - 中间件配置
  - 静态文件和媒体文件设置
  - AI API配置
  - 安全设置

- **`urls.py`** - 主URL路由配置
  - 应用URL包含配置
  - 管理后台URL
  - 静态文件服务配置

- **`wsgi.py`** - WSGI服务器配置
  - 生产环境部署配置
  - Web服务器网关接口

- **`asgi.py`** - ASGI服务器配置
  - 异步服务器网关接口
  - 支持WebSocket等异步功能

- **`__init__.py`** - Python包标识文件

## 🏗️ 配置架构

### 应用注册顺序
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 项目应用
    'core',              # 核心共享模块
    'accounts',          # 用户管理
    'pets',              # 宠物档案管理
    'consultations',     # AI咨询系统
    'logs',              # 宠物日志记录
]
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

## 🔧 主要配置项

### 数据库配置
- **开发环境**: SQLite3 (`db.sqlite3`)
- **生产环境**: PostgreSQL (推荐)

### AI集成配置
- DeepSeek API密钥配置
- AI模型参数设置
- 请求频率限制

### 安全配置
- CSRF保护
- 跨域资源共享
- 会话安全设置
- 密码验证规则

### 静态文件配置
- 静态文件收集路径
- 媒体文件上传路径
- 文件服务配置

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

## 🔒 安全考虑

### 敏感信息保护
- SECRET_KEY环境变量化
- 数据库密码环境变量
- API密钥安全存储

### 访问控制
- ALLOWED_HOSTS限制
- CORS配置
- 会话超时设置

## 📈 性能优化

### 缓存配置
- Redis缓存配置
- 会话缓存设置
- 静态文件缓存

### 数据库优化
- 连接池配置
- 查询优化设置
- 索引策略

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

---

**创建日期**: 2025年5月25日  
**最后更新**: 2025年5月25日  
