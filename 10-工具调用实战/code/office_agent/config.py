#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第10篇配套完整项目代码 · config.py
工具调用实战：打造自动化办公智能体
==========================================================================
"""

import os

# 大模型配置
MODEL_API_KEY = os.getenv("API_KEY", "mock-api-key")
MODEL_BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")

# 嵌入模型
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "text-embedding-ada-002")

# 运行模式
USE_MOCK = os.getenv("USE_MOCK", "true").lower() in ("1", "true", "yes")
VERBOSE = True

# RAG参数
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
TOP_K = 3

# 工具安全配置
SAFE_EVAL_MAX_LENGTH = 100   # 计算表达式最大长度
