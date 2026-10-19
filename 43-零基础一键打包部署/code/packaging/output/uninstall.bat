@echo off
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
