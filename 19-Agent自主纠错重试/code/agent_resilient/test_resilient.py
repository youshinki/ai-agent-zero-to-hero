#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第19篇配套 · test_resilient.py
验证自主纠错重试：
  1. 读取不存在的文件 → 首次失败 → 反思修正路径 → 重试成功
  2. 正常多步任务 → 全部成功
  3. 无法修复的任务 → 重试耗尽后兜底，不崩溃

运行: python test_resilient.py
"""

import os

from agent_core import agent


def main():
    print("=" * 64)
    print("🧪 自主纠错重试测试")
    print("=" * 64)

    # 准备一个存在的文件（供修正后读取）
    os.makedirs("auto_task_log", exist_ok=True)
    with open("auto_task_log/task_record.txt", "w", encoding="utf-8") as f:
        f.write("==== 历史任务记录 ====\n上次执行：每日复盘成功。\n")

    # 场景1：读取不存在的文件（应触发纠错重试）
    print("\n【场景1】读取不存在的文件 → 应自动修正")
    r1 = agent.run("读取 missing_file.txt 的内容并总结", [])
    print(f"\n  成功步骤：{sum(1 for x in r1['execute_log'] if x['success'])}/{len(r1['execute_log'])}")
    print(f"  最终答案：{r1['final_answer'][:150].replace(chr(10), ' ')}...")

    # 场景2：正常多步任务
    print("\n" + "=" * 64)
    print("【场景2】正常多步任务")
    r2 = agent.run("计算 (100-20)*3 并保存到 calc_result.txt：自动计算完成", [])
    print(f"\n  步骤数：{r2['step_count']}  失败数：{r2['fail_count']}")
    for log in r2["execute_log"]:
        print(f"   步骤{log['step']} [{log['tool_name']}] success={log['success']}")

    # 场景3：兜底不崩溃
    print("\n" + "=" * 64)
    print("【场景3】异常任务兜底")
    r3 = agent.run("做一个无法完成的神秘操作", [])
    print(f"\n  是否崩溃：否")
    print(f"  最终答案：{r3['final_answer'][:100].replace(chr(10), ' ')}...")

    # 校验：场景1的日志应显示重试痕迹（error 非空但 success）
    retried = any(log.get("retried") for log in r1["execute_log"])
    print(f"\n{'='*64}")
    print(f"🔍 是否发生过失败重试：{'✅ 是' if retried else '❌ 否'}")
    print("\n✅ 自主纠错重试测试完成")


if __name__ == "__main__":
    main()
