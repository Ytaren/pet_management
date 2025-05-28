@echo off
REM 智能宠物管理系统 - 快速启动
chcp 65001 >nul
title 宠物管理系统 - 快速启动

set "PROJECT_DIR=%~dp0pet_site"
cd /d "%PROJECT_DIR%"

echo 🐾 启动宠物管理系统...
echo.

REM 快速检查
if not exist manage.py (
    echo ❌ 项目文件不完整
    pause & exit /b 1
)

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装
    pause & exit /b 1
)

REM 安装依赖（如果需要）
python -c "import django" 2>nul
if %errorlevel% neq 0 (
    echo 📦 安装依赖...
    pip install -r ..\requirements.txt
)

REM 数据库迁移
python manage.py migrate >nul 2>&1

REM 启动服务器
echo ✅ 启动服务器: http://127.0.0.1:8000/
echo.
python manage.py runserver

pause
