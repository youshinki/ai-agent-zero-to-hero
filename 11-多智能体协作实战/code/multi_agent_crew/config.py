#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第11篇配套完整项目代码 · config.py
多智能体协作实战：用CrewAI搭建团队分工Agent
==========================================================================
"""

import os

# 模型配置
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")
API_KEY = os.getenv("API_KEY", "mock-api-key")
BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")

# 运行模式
# USE_MOCK=True：使用内置的CrewAI兼容模拟引擎，无需安装crewai、无需API
# USE_MOCK=False：使用真实 crewai + 大模型
USE_MOCK = os.getenv("USE_MOCK", "true").lower() in ("1", "true", "yes")

# 团队配置
VERBOSE = True
MAX_RPM = 30   # 每分钟最大请求数（避免限流）


def get_llm():
    """返回真实LLM（仅真实模式下调用）"""
    from crewai import LLM
    return LLM(model=MODEL_NAME, api_key=API_KEY, base_url=BASE_URL)
