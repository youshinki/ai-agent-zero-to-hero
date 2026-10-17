# ===== scheduler_task.py：定时任务模块 =====

from apscheduler.schedulers.background import BackgroundScheduler
from agent_core import agent
import json
import os
# 记忆文件路径
MEMORY_DIR = "chat_memory"
MEMORY_FILE = os.path.join(MEMORY_DIR, "history.json")
# 初始化后台调度器
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
# 读取历史记忆
def load_all_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
# 1. 每日自动复盘任务
def daily_auto_review():
    print("[定时任务执行] 每日AI自动复盘")
    history = load_all_memory()
    task_prompt = """
请结合我们今日所有对话，帮我完成一次**每日工作复盘**
输出格式：
1. 今日核心事项总结
2. 收获与进步
3. 存在不足
4. 明日优化计划
"""
    # 调用带记忆的Agent推理
    res = agent.run_with_history(task_prompt, history)
    save_auto_task_record("【每日自动复盘】", task_prompt, res["final_result"])
# 2. 每周总结任务
def weekly_summary():
    print("[定时任务执行] 每周AI总结")
    history = load_all_memory()
    task_prompt = """
请基于本周全部对话记录，生成一份**周度工作总结与成长分析**
包含：本周核心成果、知识沉淀、问题汇总、下周规划
"""
    res = agent.run_with_history(task_prompt, history)
    save_auto_task_record("【每周自动总结】", task_prompt, res["final_result"])
# 自动任务结果存档
def save_auto_task_record(task_name, prompt, result):
    os.makedirs("auto_task_log", exist_ok=True)
    with open("auto_task_log/task_record.txt", "a", encoding="utf-8") as f:
        f.write(f"\n===={task_name}====\n【任务指令】{prompt}\n【执行结果】\n{result}\n")
# 注册定时任务
def start_scheduler():
    # 每天 22:30 自动复盘
    scheduler.add_job(daily_auto_review, "cron", hour=22, minute=30)
    # 每周日 23:00 周总结
    scheduler.add_job(weekly_summary, "cron", day_of_week=6, hour=23, minute=0)
    scheduler.start()
    print("✅ AI Agent 全自动定时任务服务启动成功！")
# 动态关闭任务
def shutdown_scheduler():
    scheduler.shutdown()
    print("定时任务服务已关闭")
