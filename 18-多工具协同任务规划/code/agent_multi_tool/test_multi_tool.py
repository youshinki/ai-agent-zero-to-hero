#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第18篇配套 · test_multi_tool.py
演示文章第七章的复杂复合任务全自动执行

运行: python test_multi_tool.py
"""

import os

from agent_core import agent


def main():
    print("=" * 64)
    print("🧪 多工具协同任务规划测试")
    print("=" * 64)

    # 清理旧产物
    for f in ["data_summary.txt"]:
        if os.path.exists(f):
            os.remove(f)

    # 文章测试任务
    task = ("计算 (512-128)*4 的结果，根据计算结果撰写一段数据分析总结，"
            "最后把总结内容保存到 data_summary.txt 文件中")

    print(f"\n📌 用户任务：{task}\n")
    result = agent.run(task, [])

    print(f"\n{'='*64}")
    print(f"多步骤：{result['multi_step']}  步骤数：{result.get('step_count', 1)}")
    print(f"{'='*64}")

    if result.get("execute_log"):
        print("\n📋 执行日志：")
        for log in result["execute_log"]:
            print(f"\n  步骤{log['step']}：{log['step_desc']}")
            print(f"    工具：{log['tool_name']}")
            print(f"    结果：{str(log['result'])[:120].replace(chr(10), ' ')}")

    print(f"\n📤 最终交付：\n{result['final_answer']}")

    # 校验
    print(f"\n{'='*64}")
    print("📂 文件产物校验：")
    if os.path.exists("data_summary.txt"):
        with open("data_summary.txt", encoding="utf-8") as f:
            content = f.read()
        print(f"   ✅ data_summary.txt 已生成（{len(content)}字）")
        print(f"   📄 内容预览：{content[:120]}...")
    else:
        print("   ❌ data_summary.txt 未生成")

    # 单步任务兼容测试
    print(f"\n{'='*64}")
    print("🔁 单步任务兼容测试：")
    r2 = agent.run("计算 1+2+3+4+5", [])
    print(f"   multi_step={r2['multi_step']}")
    print(f"   结果：{r2['final_answer'][:100]}...")

    assert os.path.exists("data_summary.txt"), "应生成最终文件"
    print("\n✅ 多工具协同测试通过")


if __name__ == "__main__":
    main()
