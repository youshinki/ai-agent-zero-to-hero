# 第43篇配套代码：零基础一键打包部署
# Windows客户端/本地服务无门槛封装
# 运行：python 01_package_deploy.py

import os
import json
from datetime import datetime

# ========== 打包部署方案 ==========
class PackageDeploy:
    """一键打包部署方案"""
    
    @staticmethod
    def generate_setup_script(project_name="AI_Agent_App"):
        """生成安装脚本"""
        return f"""@echo off
echo ========================================
echo   {project_name} - 一键安装部署脚本
echo ========================================
echo.

echo [1/4] 检测Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python环境正常

echo [2/4] 创建虚拟环境...
if exist venv (
    echo [OK] 虚拟环境已存在
) else (
    python -m venv venv
    echo [OK] 虚拟环境创建完成
)

echo [3/4] 安装依赖...
call venv\\Scripts\\activate
pip install -r requirements.txt -q
echo [OK] 依赖安装完成

echo [4/4] 初始化配置...
if not exist .env (
    copy .env.example .env
    echo [说明] 请编辑.env文件填入你的API密钥
)
echo [OK] 配置初始化完成

echo.
echo ========================================
echo  ✅ 安装完成！
echo.
echo 启动命令：python main.py
echo 访问地址：http://localhost:8000
echo ========================================
pause
"""
    
    @staticmethod
    def generate_uninstall_script():
        return """@echo off
echo ========================================
echo   卸载 {project_name}
echo ========================================
echo.
echo 正在删除虚拟环境...
if exist venv (
    rmdir /s /q venv
    echo [OK] 虚拟环境已删除
)

echo 正在删除缓存文件...
if exist __pycache__ (
    rmdir /s /q __pycache__
)
echo [OK] 缓存已清理

echo.
echo ✅ 卸载完成！
pause
"""
    
    @staticmethod
    def generate_startup_script(is_windows=True):
        if is_windows:
            return """@echo off
chcp 65001 >nul
echo ========================================
echo   启动 AI Agent 应用
echo ========================================
echo.

call venv\\Scripts\\activate
echo [启动] 正在启动服务...
python main.py

if %errorlevel% neq 0 (
    echo [错误] 启动失败，请检查日志
    pause
)
"""
        else:
            return """#!/bin/bash
echo "启动 AI Agent 应用"
source venv/bin/activate
python main.py
"""

# ========== 配置检查 ==========
class ConfigValidator:
    """配置检查器"""
    
    @staticmethod
    def check_environment():
        """检查运行环境"""
        checks = []
        
        # Python版本
        import sys
        py_version = sys.version_info
        checks.append({
            "item": "Python版本",
            "status": "✅" if py_version.major >= 3 and py_version.minor >= 8 else "❌",
            "current": f"{py_version.major}.{py_version.minor}.{py_version.micro}"
        })
        
        # 依赖检查
        deps = ["openai", "fastapi", "uvicorn", "chromadb"]
        for dep in deps:
            try:
                __import__(dep)
                checks.append({"item": dep, "status": "✅", "current": "已安装"})
            except ImportError:
                checks.append({"item": dep, "status": "❌", "current": "未安装"})
        
        # .env文件检查
        checks.append({
            "item": ".env配置文件",
            "status": "✅" if os.path.exists(".env") else "⚠️",
            "current": "存在" if os.path.exists(".env") else "缺失（将从.env.example创建）"
        })
        
        return checks

# ========== 启动包装器 ==========
class AppWrapper:
    """应用启动包装器"""
    
    @staticmethod
    def create_main_entry(port=8000):
        return """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"AI Agent 应用入口（生产级启动文件）\"\"\"

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Agent API",
    version="1.0.0",
    docs_url="/docs"  # 生产环境可关闭
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": __import__("datetime").datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port={port},
        reload=False,  # 生产环境关闭热重载
        log_level="info"
    )
"""

if __name__ == "__main__":
    print("=" * 60)
    print("📦 零基础一键打包部署")
    print("=" * 60)
    
    print("\n1️⃣ 环境检查")
    print("-" * 40)
    checks = ConfigValidator.check_environment()
    for c in checks:
        print(f"  {c['status']} {c['item']}：{c['current']}")
    
    print("\n2️⃣ Windows安装脚本 (install.bat)")
    print("-" * 40)
    print(PackageDeploy.generate_setup_script()[:300] + "...")
    
    print("\n3️⃣ 启动脚本 (start.bat / start.sh)")
    print("-" * 40)
    print("Windows版本：")
    print(PackageDeploy.generate_startup_script(is_windows=True))
    
    print("\n4️⃣ 主入口文件 (main.py)")
    print("-" * 40)
    print(AppWrapper.create_main_entry(port=8000))
    
    print("\n✅ 打包部署完成！用户只需：")
    print("  1. 双击 install.bat（自动安装环境）")
    print("  2. 编辑 .env 填入API密钥")
    print("  3. 双击 start.bat（启动服务）")
    print("  4. 浏览器访问 http://localhost:8000")
