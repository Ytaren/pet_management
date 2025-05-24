@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title 智能宠物管理系统

echo ================================================================
echo 🐾 智能宠物管理系统 - 启动脚本
echo ================================================================
echo.

REM 获取脚本所在目录的绝对路径
set "SCRIPT_DIR=%~dp0"
REM 移除末尾的反斜杠
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM 项目目录是脚本目录下的pet_site文件夹
set "PROJECT_DIR=%SCRIPT_DIR%\pet_site"

REM 检查项目目录是否存在
if not exist "%PROJECT_DIR%" (
    echo ❌ 错误：找不到项目目录 pet_site
    echo    当前脚本位置：%SCRIPT_DIR%
    echo    预期项目目录：%PROJECT_DIR%
    echo    请确保此脚本位于项目根目录下
    pause
    exit /b 1
)

REM 切换到项目目录
cd /d "%PROJECT_DIR%"

echo 📍 当前目录: %CD%
echo.

echo 🔍 检查Python环境...
python --version 2>nul
if !errorlevel! neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo    请确保已安装Python并添加到系统PATH环境变量
    pause
    exit /b 1
)

echo ✅ Python环境正常
echo.

echo 📦 检查依赖包...
python -c "import django" 2>nul
if !errorlevel! neq 0 (
    echo 📥 安装依赖包...
    REM 检查requirements.txt是否存在（在项目根目录）
    if exist "%SCRIPT_DIR%\requirements.txt" (
        echo    从 requirements.txt 安装依赖...
        pip install -r "%SCRIPT_DIR%\requirements.txt"
    ) else (
        echo    安装基础依赖包...
        pip install django requests
    )
    if !errorlevel! neq 0 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖包安装成功
) else (
    echo ✅ 依赖包已安装
)
echo.

echo 🗄️ 执行数据库迁移...
python manage.py migrate
if !errorlevel! neq 0 (
    echo ❌ 数据库迁移失败
    pause
    exit /b 1
)
echo.

echo 🌟 启动Django服务器...
echo 📱 服务器地址: http://127.0.0.1:8000/
echo 🛑 按 Ctrl+C 停止服务器
echo.
python manage.py runserver

echo.
echo 服务器已停止
pause

