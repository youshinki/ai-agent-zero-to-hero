#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第13篇配套完整项目代码 · config.py
Agent前端可视化：搭建极简AI对话网页
==========================================================================
"""

import os

MODEL_API_KEY = os.getenv("API_KEY", "mock-api-key")
MODEL_BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")

USE_MOCK = os.getenv("USE_MOCK", "true").lower() in ("1", "true", "yes")
MAX_THOUGHT_STEPS = 3
MAX_RETRY = 3

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
