#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第16篇配套 · test_scheduler.py
验证：任务注册、手动触发、结果存档

运行: python test_scheduler.py
"""

import os
import shutil

from fastapi.testclient import TestClient

import config
# 使用独立测试目录，避免污染真实数据
config.MEMORY_DIR = "chat_memory_test"
config.MEMORY_FILE = os.path.join(config.MEMORY_DIR, "history.json")
config.AUTO_TASK_LOG_DIR = "auto_task_log_test"
config.AUTO_TASK_LOG_FILE = os.path.join(config.AUTO_TASK_LOG_DIR, "task_record.txt")

import scheduler_task
scheduler_task.MEMORY_FILE = config.MEMORY_FILE
scheduler_task.AUTO_TASK_LOG_DIR = config.AUTO_TASK_LOG_DIR
scheduler_task.AUTO_TASK_LOG_FILE = config.AUTO_TASK_LOG_FILE

import main
main.MEMORY_DIR = config.MEMORY_DIR
main.MEMORY_FILE = config.MEMORY_FILE

client = TestClient(main.app)


def main_test():
    shutil.rmtree(config.MEMORY_DIR, ignore_errors=True)
    shutil.rmtree(config.AUTO_TASK_LOG_DIR, ignore_errors=True)
    os.makedirs(config.MEMORY_DIR, exist_ok=True)

    print("=" * 62)
    print("🧪 定时任务测试")
    print("=" * 62)

    # 准备一些历史记忆
    import json
    history = [
        {"role": "user", "content": "我是一名AI开发者，擅长Agent工程化"},
        {"role": "assistant", "content": "好的，已记住。"},
        {"role": "user", "content": "今天完成了RAG知识库模块"},
        {"role": "assistant", "content": "进展不错。"},
    ]
    with open(config.MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    # 1. 查看任务注册情况
    r = client.get("/api/agent/jobs").json()
    print(f"\n[GET /api/agent/jobs] 已注册 {len(r['jobs'])} 个任务：")
    for j in r["jobs"]:
        print(f"   - {j['id']}: {j['trigger']} | 下次运行: {j['next_run']}")

    # 2. 手动触发每日复盘
    r = client.post("/api/agent/jobs/daily").json()
    print(f"\n[POST /api/agent/jobs/daily] {r['msg']}")
    print(f"   结果预览：{r['result'][:80]}...")

    # 3. 手动触发每周总结
    r = client.post("/api/agent/jobs/weekly").json()
    print(f"\n[POST /api/agent/jobs/weekly] {r['msg']}")
    print(f"   结果预览：{r['result'][:80]}...")

    # 4. 校验存档
    log_exists = os.path.exists(config.AUTO_TASK_LOG_FILE)
    print(f"\n[存档校验] 日志文件存在：{log_exists}")
    if log_exists:
        with open(config.AUTO_TASK_LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"   记录条数：{content.count('====') // 2}")
        print(f"   包含每日复盘：{'每日自动复盘' in content}")
        print(f"   包含每周总结：{'每周自动总结' in content}")

    # 5. 健康检查
    r = client.get("/health")
    print(f"\n[GET /health] {r.json()}")

    assert log_exists, "任务记录应被存档"
    print("\n✅ 定时任务测试全部通过")


if __name__ == "__main__":
    main_test()
