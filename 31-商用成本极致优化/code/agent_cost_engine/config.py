#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第31篇配套完整项目代码 · config.py
商用成本极致优化：API计费节流，砍掉70%开销
==========================================================================
"""

import os

# ---------------- 模型价格（每1K token，单位：元） ----------------
MODEL_PRICES = {
    "gpt-4":            {"input": 0.21, "output": 0.42, "level": "high"},
    "gpt-3.5-turbo":    {"input": 0.0035, "output": 0.007, "level": "mid"},
    "deepseek-chat":    {"input": 0.002, "output": 0.004, "level": "low"},
    "qwen-turbo":       {"input": 0.0015, "output": 0.003, "level": "low"},
}

# ---------------- 缓存配置 ----------------
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
EMBEDDING_CACHE_SIZE = 1000

# ---------------- 预算配置 ----------------
DAILY_BUDGET_YUAN = float(os.getenv("DAILY_BUDGET_YUAN", "50"))
MONTHLY_BUDGET_YUAN = float(os.getenv("MONTHLY_BUDGET_YUAN", "1000"))

# ---------------- 节流配置 ----------------
MAX_INPUT_TOKENS = 2000       # 单次输入上限（超出则压缩）
PROMPT_COMPRESS_RATIO = 0.5   # 压缩目标比例
BATCH_SIZE = 5                # 批量合并请求数
ENABLE_CACHE = True           # 是否启用缓存
ENABLE_ROUTING = True         # 是否启用模型路由
