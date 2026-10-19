#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第16篇配套完整项目代码 · scheduler_task.py
定时任务核心服务（APScheduler）：

  1. 每日 22:30 自动复盘
  2. 每周日 23:00 周度总结
  3. 所有自动任务结果永久存档

设计要点（文章第五章）：
  - 后台异步运行，不阻塞接口
  - 自动读取历史记忆，复盘真实
  - 自动日志存档
  - 支持任意时间、任意任务扩展
==========================================================================
"""

import json
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from agent_core import agent
from config import (
    MEMORY_DIR, MEMORY_FILE, AUTO_TASK_LOG_DIR, AUTO_TASK_LOG_FILE,
    TIMEZONE, DAILY_REVIEW_HOUR, DAILY_REVIEW_MINUTE,
    WEEKLY_SUMMARY_DAY, WEEKLY_SUMMARY_HOUR, WEEKLY_SUMMARY_MINUTE,
)


# 初始化后台调度器
scheduler = BackgroundScheduler(timezone=TIMEZONE)
_scheduler_started = False


# ----------------------------------------------------------------------
# 工具函数
# ----------------------------------------------------------------------

def load_all_memory() -> list:
    """读取历史记忆"""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_auto_task_record(task_name: str, prompt: str, result: str):
    """自动任务结果存档 —— 永久留存"""
    os.makedirs(AUTO_TASK_LOG_DIR, exist_ok=True)
    with open(AUTO_TASK_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"==== {task_name} ====\n")
        f.write(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"【任务指令】{prompt}\n")
        f.write(f"【执行结果】\n{result}\n")


# ----------------------------------------------------------------------
# 任务定义
# ----------------------------------------------------------------------

def daily_auto_review():
    """每日自动复盘任务"""
    print(f"[定时任务执行] 每日AI自动复盘 @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    history = load_all_memory()

    task_prompt = """请结合我们今日所有对话，帮我完成一次**每日工作复盘**
输出格式：
1. 今日核心事项总结
2. 收获与进步
3. 存在不足
4. 明日优化计划
"""

    res = agent.run_with_history(task_prompt, history)
    save_auto_task_record("【每日自动复盘】", task_prompt, res["final_result"])
    print("[定时任务完成] 每日自动复盘")
    return res["final_result"]


def weekly_summary():
    """每周总结任务"""
    print(f"[定时任务执行] 每周AI总结 @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    history = load_all_memory()

    task_prompt = """请基于本周全部对话记录，生成一份**周度工作总结与成长分析**
包含：本周核心成果、知识沉淀、问题汇总、下周规划
"""

    res = agent.run_with_history(task_prompt, history)
    save_auto_task_record("【每周自动总结】", task_prompt, res["final_result"])
    print("[定时任务完成] 每周自动总结")
    return res["final_result"]


def custom_auto_task(name: str, prompt: str):
    """自定义任意自动任务（扩展能力）"""
    history = load_all_memory()
    res = agent.run_with_history(prompt, history)
    save_auto_task_record(f"【{name}】", prompt, res["final_result"])
    return res["final_result"]


# ----------------------------------------------------------------------
# 调度器生命周期
# ----------------------------------------------------------------------

def start_scheduler():
    """注册并启动定时任务（全局只启动一次）"""
    global _scheduler_started
    if _scheduler_started:
        return

    # 每天 22:30 自动复盘
    scheduler.add_job(
        daily_auto_review, "cron",
        hour=DAILY_REVIEW_HOUR, minute=DAILY_REVIEW_MINUTE,
        id="daily_review", replace_existing=True,
    )

    # 每周日 23:00 周总结
    scheduler.add_job(
        weekly_summary, "cron",
        day_of_week=WEEKLY_SUMMARY_DAY,
        hour=WEEKLY_SUMMARY_HOUR, minute=WEEKLY_SUMMARY_MINUTE,
        id="weekly_summary", replace_existing=True,
    )

    scheduler.start()
    _scheduler_started = True
    print("✅ AI Agent 全自动定时任务服务启动成功！")
    for job in scheduler.get_jobs():
        print(f"   - {job.id}: {job.trigger}")


def shutdown_scheduler():
    """动态关闭任务"""
    global _scheduler_started
    if _scheduler_started:
        scheduler.shutdown(wait=False)
        _scheduler_started = False
        print("定时任务服务已关闭")


def list_jobs() -> list:
    """查看已注册任务"""
    return [{"id": j.id, "next_run": str(j.next_run_time), "trigger": str(j.trigger)}
            for j in scheduler.get_jobs()]


if __name__ == "__main__":
    # 独立运行（不启动Web服务）时，直接演示触发两个任务
    print("=" * 60)
    print("⏰ 定时任务独立演示（立即触发一次，不等待cron时间）")
    print("=" * 60)
    print("\n--- 触发每日复盘 ---")
    daily_auto_review()
    print("\n--- 触发每周总结 ---")
    weekly_summary()
    print(f"\n📄 任务记录已写入：{AUTO_TASK_LOG_FILE}")
