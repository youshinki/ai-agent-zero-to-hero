#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第12篇配套完整项目代码 · config.py
Agent服务化部署：把智能体包装成API接口
==========================================================================
"""

import os

# 大模型基础配置
MODEL_API_KEY = os.getenv("API_KEY", "mock-api-key")
MODEL_BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")

# Agent运行参数
MAX_THOUGHT_STEPS = 3
MAX_RETRY = 3

# 运行模式
USE_MOCK = os.getenv("USE_MOCK", "true").lower() in ("1", "true", "yes")
VERBOSE = os.getenv("VERBOSE", "true").lower() in ("1", "true", "yes")

# 服务配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
