#!/bin/bash
# Linux/macOS 启动脚本
set -e
if [ ! -d "venv" ]; then
  echo "未找到虚拟环境，请先执行: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi
source venv/bin/activate
python main.py
