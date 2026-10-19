# 一键打包部署说明

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
