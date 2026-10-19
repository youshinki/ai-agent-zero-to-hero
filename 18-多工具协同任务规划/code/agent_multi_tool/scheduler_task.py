#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第18篇配套完整项目代码 · scheduler_task.py
定时任务（兼容第16篇）：基于多工具协同Agent
==========================================================================
"""

import json
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from agent_core import agent
from config import MEMORY_FILE, AUTO_TASK_LOG_DIR, AUTO_TASK_LOG_FILE, TIMEZONE

scheduler = BackgroundScheduler(timezone=TIMEZONE)
_started = False


def load_all_memory() -> list:
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_auto_task_record(task_name: str, prompt: str, result: str):
    os.makedirs(AUTO_TASK_LOG_DIR, exist_ok=True)
    with open(AUTO_TASK_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n==== {task_name} ====\n")
        f.write(f"执行时间：{datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write(f"【任务指令】{prompt}\n【执行结果】\n{result}\n")


def daily_auto_review():
    prompt = "请结合今日对话完成每日复盘（可拆解为多步：分析→总结→归档）"
    res = agent.run(prompt, load_all_memory())
    save_auto_task_record("【每日自动复盘】", prompt, res["final_answer"])
    return res["final_answer"]


def weekly_summary():
    prompt = "请基于本周对话生成周度总结与成长分析"
    res = agent.run(prompt, load_all_memory())
    save_auto_task_record("【每周自动总结】", prompt, res["final_answer"])
    return res["final_answer"]


def start_scheduler():
    global _started
    if _started:
        return
    scheduler.add_job(daily_auto_review, "cron", hour=22, minute=30,
                      id="daily_review", replace_existing=True)
    scheduler.add_job(weekly_summary, "cron", day_of_week=6, hour=23, minute=0,
                      id="weekly_summary", replace_existing=True)
    scheduler.start()
    _started = True
    print("✅ 定时任务服务启动成功（多工具协同版）")


def shutdown_scheduler():
    global _started
    if _started:
        scheduler.shutdown(wait=False)
        _started = False
