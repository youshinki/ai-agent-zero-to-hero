@echo off
chcp 65001 >nul
echo ========================================
echo   AI_Agent_App - 一键安装部署
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
call venv\Scripts\activate
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
