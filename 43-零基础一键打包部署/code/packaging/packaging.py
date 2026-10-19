#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第43篇配套完整项目代码 · packaging.py
零基础一键打包部署（Windows 客户端/本地服务）：
  1. install.bat / start.bat / uninstall.bat
  2. 环境检测脚本
  3. PyInstaller 打包配置（.spec）
  4. 配置向导（.env 生成）
  5. 启动入口（main.py）

运行: python packaging.py     # 生成安装包到 output/
"""

import os

OUTPUT_DIR = "output"


# ======================================================================
# 一、Windows 安装脚本
# ======================================================================

def install_bat(app_name="AI_Agent_App") -> str:
    return f"""@echo off
chcp 65001 >nul
echo ========================================
echo   {app_name} - 一键安装部署
echo ========================================
echo.

echo [1/4] 检测 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo 下载地址：https://www.python.org/downloads/
    echo 安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)
echo [OK] Python 环境正常

echo [2/4] 创建虚拟环境...
if exist venv (
    echo [OK] 虚拟环境已存在
) else (
    python -m venv venv
    echo [OK] 虚拟环境创建完成
)

echo [3/4] 安装依赖...
call venv\\Scripts\\activate
if exist requirements.txt (
    pip install -r requirements.txt -q
    echo [OK] 依赖安装完成
) else (
    echo [跳过] 未找到 requirements.txt
)

echo [4/4] 初始化配置...
if not exist .env (
    copy .env.example .env >nul 2>&1
    echo [说明] 请编辑 .env 文件，填入你的 API 密钥
)

echo.
echo ========================================
echo   安装完成！
echo.
echo   1. 编辑 .env 填写 API 密钥
echo   2. 双击 start.bat 启动服务
echo   3. 浏览器访问 http://localhost:8000
echo ========================================
pause
"""


def start_bat(app_name="AI_Agent_App") -> str:
    return f"""@echo off
chcp 65001 >nul
echo ========================================
echo   启动 {app_name}
echo ========================================
echo.

if not exist venv (
    echo [错误] 未找到虚拟环境，请先运行 install.bat
    pause
    exit /b 1
)

call venv\\Scripts\\activate
echo [启动] 正在启动服务...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 启动失败，请检查：
    echo   1. .env 是否配置正确
    echo   2. 端口 8000 是否被占用
    pause
)
"""


def uninstall_bat() -> str:
    return """@echo off
chcp 65001 >nul
echo ========================================
echo   卸载 AI Agent 应用
echo ========================================
echo.
echo 正在删除虚拟环境...
if exist venv (
    rmdir /s /q venv
    echo [OK] 虚拟环境已删除
)
echo 正在清理缓存...
if exist __pycache__ rmdir /s /q __pycache__
echo.
echo 卸载完成！（.env 与数据目录已保留）
pause
"""


def start_sh() -> str:
    return """#!/bin/bash
# Linux/macOS 启动脚本
set -e
if [ ! -d "venv" ]; then
  echo "未找到虚拟环境，请先执行: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi
source venv/bin/activate
python main.py
"""


# ======================================================================
# 二、环境检测
# ======================================================================

def env_check() -> str:
    return '''#!/usr/bin/env python3
"""环境检测脚本：python check_env.py"""
import importlib
import os
import sys

def main():
    print("=" * 50)
    print("🔍 环境检测")
    print("=" * 50)
    ok = True
    # Python 版本
    v = sys.version_info
    status = "✅" if (v.major, v.minor) >= (3, 10) else "❌"
    print(f"{status} Python {v.major}.{v.minor}.{v.micro}（需要 3.10+）")
    ok = ok and (v.major, v.minor) >= (3, 10)
    # 依赖
    for dep in ["fastapi", "uvicorn", "pydantic", "numpy"]:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep} 已安装")
        except ImportError:
            print(f"❌ {dep} 未安装 → pip install {dep}")
            ok = False
    # .env
    if os.path.exists(".env"):
        print("✅ .env 配置文件存在")
    else:
        print("⚠️ .env 不存在，请复制 .env.example 并填写")
    print("\\n" + ("✅ 环境就绪" if ok else "❌ 请先修复上述问题"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
'''


# ======================================================================
# 三、PyInstaller 配置
# ======================================================================

def pyinstaller_spec(app_name="AI_Agent_App") -> str:
    return f"""# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置：pyinstaller {app_name}.spec
# 生成单文件 exe：dist/{app_name}.exe

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('knowledge_base', 'knowledge_base'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'uvicorn', 'fastapi', 'pydantic', 'numpy',
        'apscheduler', 'json', 'sqlite3',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)
"""


# ======================================================================
# 四、启动入口
# ======================================================================

def main_py() -> str:
    return '''#!/usr/bin/env python3
"""启动入口（生产模式）"""
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 确保打包后能找到本地模块
if getattr(sys, "frozen", False):
    base = os.path.dirname(sys.executable)
    sys.path.insert(0, base)

app = FastAPI(title="AI Agent 服务", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "running", "service": "AI Agent"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/chat")
async def chat(payload: dict):
    task = payload.get("task", "")
    if not task:
        return {"success": False, "answer": "请输入问题。"}
    return {"success": True, "answer": f"已收到问题：{task}（示例实现）"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"服务启动：http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
'''


# ======================================================================
# 五、打包 README
# ======================================================================

def build_readme() -> str:
    return """# 一键打包部署说明

## Windows 用户（最简单）

1. 双击 `install.bat` 安装环境
2. 编辑 `.env` 填写 API 密钥
3. 双击 `start.bat` 启动
4. 浏览器打开 `http://localhost:8000`

## Linux / macOS 用户

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python check_env.py
bash start.sh
```

## 打包成 exe（可选）

```bash
pip install pyinstaller
pyinstaller AI_Agent_App.spec
# 产物：dist/AI_Agent_App.exe
```

## 常见问题

| 问题 | 处理 |
|------|------|
| 未检测到 Python | 安装 Python 3.10+，勾选 Add to PATH |
| 端口被占用 | 改 .env 中 PORT=8001 |
| 启动闪退 | 命令行运行 python main.py 看报错 |
| 双击 bat 无反应 | 右键"以管理员身份运行" |
"""


def generate_package(app_name="AI_Agent_App") -> list:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = {
        "install.bat": install_bat(app_name),
        "start.bat": start_bat(app_name),
        "uninstall.bat": uninstall_bat(),
        "start.sh": start_sh(),
        "check_env.py": env_check(),
        f"{app_name}.spec": pyinstaller_spec(app_name),
        "main.py": main_py(),
        "README.md": build_readme(),
    }
    paths = []
    for name, content in files.items():
        path = os.path.join(OUTPUT_DIR, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        paths.append(path)
    return paths


if __name__ == "__main__":
    print("=" * 60)
    print("📦 生成一键打包部署包")
    print("=" * 60)
    for p in generate_package():
        print(f"   ✅ {p}（{os.path.getsize(p)}字节）")
