#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第20篇配套 · scheduler_task.py（定时任务，复用结构）"""

import json
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from agent_core import agent
from knowledge_base.kb_core import kb
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
    prompt = "今日工作复盘：核心事项、收获、不足、明日计划"
    res = agent.run(prompt, load_all_memory())
    save_auto_task_record("【每日自动复盘】", prompt, res["final_answer"])
    return res["final_answer"]


def weekly_summary():
    prompt = "本周总结与成长分析"
    res = agent.run(prompt, load_all_memory())
    save_auto_task_record("【每周自动总结】", prompt, res["final_answer"])
    return res["final_answer"]


def auto_incremental_update():
    """凌晨自动增量更新知识库"""
    print(f"[定时任务] 知识库自动增量更新 @ {datetime.now():%Y-%m-%d %H:%M}")
    log = kb.scan_all_update()
    changed = [x for x in log if x["status"] in ("updated", "deleted")]
    result = f"扫描{len(log)}个文件，变更{len(changed)}个"
    save_auto_task_record("【知识库自动增量更新】", "", result + "\n" + "\n".join(x["message"] for x in log))
    return result


def start_scheduler():
    global _started
    if _started:
        return
    scheduler.add_job(daily_auto_review, "cron", hour=22, minute=30,
                      id="daily_review", replace_existing=True)
    scheduler.add_job(weekly_summary, "cron", day_of_week=6, hour=23, minute=0,
                      id="weekly_summary", replace_existing=True)
    # 每天凌晨2点自动增量更新知识库
    scheduler.add_job(auto_incremental_update, "cron", hour=2, minute=0,
                      id="kb_auto_update", replace_existing=True)
    scheduler.start()
    _started = True
    print("✅ 定时任务服务启动成功（私有知识库版）")
