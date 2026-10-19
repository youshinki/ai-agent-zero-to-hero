#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第17篇配套完整项目代码 · config.py
自动工具调用实战：让Agent自主判断、自选工具、独立完成任务
==========================================================================
"""

import os

MODEL_API_KEY = os.getenv("API_KEY", "mock-api-key")
MODEL_BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")

USE_MOCK = os.getenv("USE_MOCK", "true").lower() in ("1", "true", "yes")
MAX_RETRY = 3

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 记忆
MEMORY_DIR = "chat_memory"
MEMORY_FILE = os.path.join(MEMORY_DIR, "history.json")
COMPRESS_THRESHOLD = int(os.getenv("COMPRESS_THRESHOLD", "20"))
KEEP_RECENT = int(os.getenv("KEEP_RECENT", "10"))

# 定时任务
AUTO_TASK_LOG_DIR = "auto_task_log"
AUTO_TASK_LOG_FILE = os.path.join(AUTO_TASK_LOG_DIR, "task_record.txt")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Shanghai")

# 工具安全配置（生产环境建议）
TOOL_WORKSPACE = os.getenv("TOOL_WORKSPACE", ".")  # 文件工具允许的根目录
MAX_EXPR_LEN = 100                                 # 计算表达式最大长度
