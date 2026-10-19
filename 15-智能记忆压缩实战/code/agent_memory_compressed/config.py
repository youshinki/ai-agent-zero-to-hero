#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第15篇配套完整项目代码 · config.py
智能记忆压缩实战：彻底解决Token爆炸，实现无限对话记忆
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

# 工业级压缩参数（可调 —— 文章第九章）
COMPRESS_THRESHOLD = int(os.getenv("COMPRESS_THRESHOLD", "20"))  # 触发压缩轮次
KEEP_RECENT = int(os.getenv("KEEP_RECENT", "10"))                # 保留最新完整轮次
