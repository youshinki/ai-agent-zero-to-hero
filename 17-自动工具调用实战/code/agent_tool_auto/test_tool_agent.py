#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第17篇配套 · test_tool_agent.py
演示文章第九章的三个测试任务：
  1. 读取文件并总结
  2. 写入文件
  3. 计算并保存

运行: python test_tool_agent.py
"""

import os

from agent_core import tool_agent


def main():
    print("=" * 62)
    print("🧪 自动工具调用 Agent 测试")
    print("=" * 62)

    # 准备一个可读文件
    os.makedirs("auto_task_log", exist_ok=True)
    with open("auto_task_log/task_record.txt", "w", encoding="utf-8") as f:
        f.write("==== 每日自动复盘 ====\n执行时间：2024-01-15 22:30\n"
                "【执行结果】今日完成RAG模块，明天继续做工具调用。\n")

    tasks = [
        "读取 auto_task_log/task_record.txt 的内容，并总结最近一次任务执行结果",
        "把这段内容写入 output.txt：今天完成了自动工具调用Agent的核心开发",
        "计算 (128+64)*3 的结果，并把结果保存到 result.txt",
        "你好，介绍一下你自己",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"\n{'─'*62}")
        print(f"📌 测试{i}：{task}")
        result = tool_agent.run(task, [])
        if result["tool_call"]:
            print(f"   🛠 工具：{result['tool_name']}")
            print(f"   📥 参数：{result['tool_args']}")
            print(f"   📤 结果：{result['tool_result'][:100]}")
        else:
            print(f"   💬 无需工具，直接回答")
        print(f"   ✅ 最终回答：{result['final_answer'][:120].replace(chr(10), ' ')}...")

    # 校验文件副作用
    print(f"\n{'='*62}")
    print("📂 文件副作用校验：")
    for path in ["output.txt", "result.txt"]:
        exists = os.path.exists(path)
        print(f"   {'✅' if exists else '❌'} {path} 已生成")
        if exists:
            with open(path, encoding="utf-8") as f:
                print(f"      内容：{f.read()[:80]}")

    print("\n✅ 自动工具调用测试完成")


if __name__ == "__main__":
    main()
