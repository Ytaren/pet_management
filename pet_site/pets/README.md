# 🐾 Pets 应用 - 宠物档案管理系统

## 📋 应用概述
Pets应用是智能宠物管理系统的核心模块，提供完整的宠物档案管理功能。支持宠物信息的CRUD操作、照片管理、动态品种选择，并与日志系统、咨询系统深度集成。

### 核心特性
- **完整档案管理** - 宠物基本信息、生理数据、健康记录
- **智能照片系统** - 照片上传、预览、安全存储
- **动态品种选择** - AJAX动态加载品种列表
- **数据集成** - 与日志、咨询系统无缝对接
- **权限控制** - 用户只能管理自己的宠物
- **响应式设计** - 适配移动端和桌面端

## 🗂️ 文件结构

### 核心文件
- **`models.py`** - 数据模型定义（Pet、Breed、VaccinationRecord）
- **`views.py`** - 视图逻辑（基于CBV的CRUD操作）
- **`forms.py`** - 表单定义和验证
- **`urls.py`** - URL路由配置
- **`admin.py`** - 后台管理界面

### 模板文件
- **`pet_list.html`** - 宠物列表页面（卡片式展示、筛选功能）
- **`pet_detail.html`** - 宠物详情页面（完整信息、快速操作）
- **`pet_form.html`** - 宠物表单页面（添加/编辑）
- **`pet_confirm_delete.html`** - 删除确认页面

## 🏗️ 数据模型

### Pet 模型
- **基本信息**: name, pet_type, breed, custom_breed
- **生理信息**: birth_date, gender, is_neutered, weight
- **附加信息**: photo, personality_notes, medical_notes
- **状态管理**: is_active, is_deleted
- **时间戳**: created_at, updated_at（继承自TimeStampedModel）

### Breed 模型
- **品种信息**: name, pet_type, description
- **状态管理**: is_active

### VaccinationRecord 模型
- **关联信息**: pet, vaccine_name
- **接种信息**: vaccination_date, next_due_date
- **记录信息**: notes, created_at

## 🔧 核心功能

### 宠物档案管理
- 自动关联当前用户的宠物
- 支持软删除保护数据
- 智能年龄计算（年/月显示）
- 完整的CRUD操作

### 智能照片管理
- 多格式图片上传支持
- 自动照片预览
- 安全文件存储
- 尺寸和大小限制

### 动态品种选择
- AJAX动态加载品种列表
- 支持自定义品种输入
- 品种与宠物类型关联

### 高级筛选功能
- 按类型、性别、绝育状态筛选
- 姓名和品种模糊搜索
- URL参数化支持

## 🔗 系统集成

### 与其他应用集成
- **Logs应用**: 宠物详情页快速添加日志
- **Consultations应用**: 宠物信息自动传递到咨询
- **Core应用**: 继承TimeStampedModel和常量定义
---
