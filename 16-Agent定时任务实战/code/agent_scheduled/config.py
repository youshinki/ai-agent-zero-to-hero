#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第16篇配套完整项目代码 · config.py
Agent定时任务实战：脱离手动触发，实现7×24小时全自动后台自主工作
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
COMPRESS_THRESHOLD = int(os.getenv("COMPRESS_THRESHOLD", "20"))
KEEP_RECENT = int(os.getenv("KEEP_RECENT", "10"))

# 定时任务配置
AUTO_TASK_LOG_DIR = "auto_task_log"
AUTO_TASK_LOG_FILE = os.path.join(AUTO_TASK_LOG_DIR, "task_record.txt")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Shanghai")

# 定时时间（可调）
DAILY_REVIEW_HOUR = int(os.getenv("DAILY_REVIEW_HOUR", "22"))
DAILY_REVIEW_MINUTE = int(os.getenv("DAILY_REVIEW_MINUTE", "30"))
WEEKLY_SUMMARY_DAY = int(os.getenv("WEEKLY_SUMMARY_DAY", "6"))  # 0=周一 ... 6=周日
WEEKLY_SUMMARY_HOUR = int(os.getenv("WEEKLY_SUMMARY_HOUR", "23"))
WEEKLY_SUMMARY_MINUTE = int(os.getenv("WEEKLY_SUMMARY_MINUTE", "0"))
