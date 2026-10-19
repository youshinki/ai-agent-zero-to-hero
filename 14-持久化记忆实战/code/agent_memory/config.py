#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第14篇配套完整项目代码 · config.py
持久化记忆实战：让AI Agent拥有长期记忆与连续对话
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

# 记忆配置
MEMORY_DIR = "chat_memory"
MEMORY_FILE = os.path.join(MEMORY_DIR, "history.json")
MAX_HISTORY_TURNS = 50   # 最多保留的历史轮数（防止无限膨胀）
