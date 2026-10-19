@echo off
chcp 65001 >nul
echo ========================================
echo   启动 AI_Agent_App
echo ========================================
echo.

if not exist venv (
    echo [错误] 未找到虚拟环境，请先运行 install.bat
    pause
    exit /b 1
)

call venv\Scripts\activate
echo [启动] 正在启动服务...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 启动失败，请检查：
    echo   1. .env 是否配置正确
    echo   2. 端口 8000 是否被占用
    pause
)
