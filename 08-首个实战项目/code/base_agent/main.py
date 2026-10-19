#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第8篇配套完整项目代码
首个实战项目：从零手写基础AI Agent
==========================================================================

本文件为 main.py —— 项目入口、Agent主运行逻辑

运行方式:
  cd base_agent
  python main.py

交互命令:
  /quit 或 /exit   退出
  /history         查看任务历史
==========================================================================
"""

import sys
import os

# 兼容从上级目录运行
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_core import BaseAgent
from config import USE_MOCK, MODEL_NAME


# ======================================================================
# 预设演示任务（无交互环境时可直接测试）
# ======================================================================

DEMO_TASKS = [
    "帮我生成本周工作总结周报，包含工作完成情况、问题和下周计划",
    "帮我写一个AI客服系统的技术方案",
]


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║           🤖 基础 AI Agent 已启动                        ║
║           《AI Agent 零基础实战》第8篇                    ║
╠══════════════════════════════════════════════════════════╣
║  能力：任务规划(CoT) → 任务执行 → 自我反思(Reflexion)   ║
║  命令：/quit 退出   /history 查看历史                    ║
╚══════════════════════════════════════════════════════════╝
""")


def main():
    print_banner()
    
    # 显示运行模式
    mode = "模拟模式（无需API，直接可跑）" if USE_MOCK else f"真实API模式（{MODEL_NAME}）"
    print(f"🔧 当前模式：{mode}\n")
    
    agent = BaseAgent()
    
    # 判断是否交互环境
    interactive = sys.stdin.isatty()
    
    if not interactive:
        # 非交互环境：运行预设演示任务
        print("（检测到非交互环境，自动运行演示任务）\n")
        for i, task in enumerate(DEMO_TASKS, 1):
            print(f"\n{'#'*60}")
            print(f"# 演示任务 {i}")
            print(f"{'#'*60}")
            result = agent.run(task)
            print(f"\n📤 最终成品：\n{result}")
        print("\n✅ 演示完成。")
        return
    
    while True:
        try:
            user_input = input("\n请输入任务（/quit 退出）：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        
        if not user_input:
            continue
        
        # 命令处理
        if user_input.lower() in ("/quit", "/exit", "quit", "exit"):
            print("感谢使用，再见！")
            break
        if user_input.lower() == "/history":
            history = agent.get_history()
            print(f"\n📚 任务历史（{len(history)}条）：")
            for i, h in enumerate(history[-5:], 1):
                print(f"  {i}. {h['task']}")
            continue
        
        # 运行Agent
        try:
            result = agent.run(user_input)
            print(f"\n{'─'*60}")
            print("📤 最终成品：")
            print(f"{'─'*60}")
            print(result)
            print(f"{'─'*60}")
        except Exception as e:
            print(f"\n❌ 执行出错：{e}")


if __name__ == "__main__":
    main()
