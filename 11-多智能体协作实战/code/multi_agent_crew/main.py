#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第11篇配套完整项目代码 · main.py
Crew启动入口（文章第八章）

用法:
  cd multi_agent_crew
  python main.py
==========================================================================
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import USE_MOCK, VERBOSE
from agents import researcher, writer, reviewer
from tasks import research_task, writing_task, review_task


def build_crew():
    """组队：把Agent和Task放进Crew"""
    if USE_MOCK:
        from crew_mock import Crew
    else:
        from crewai import Crew
    return Crew(
        agents=[researcher, writer, reviewer],
        tasks=[research_task, writing_task, review_task],
        verbose=VERBOSE,
    )


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║        👥 多智能体协作团队 已就绪                        ║
║        《AI Agent 零基础实战》第11篇                     ║
╠══════════════════════════════════════════════════════════╣
║  团队：研究员 → 撰稿人 → 审核员（顺序协作）              ║
╚══════════════════════════════════════════════════════════╝
""")
    print(f"🔧 模式：{'模拟模式（无需安装crewai/API）' if USE_MOCK else '真实 CrewAI 模式'}\n")
    
    # 交互式输入主题；非交互环境使用默认主题
    if sys.stdin.isatty():
        try:
            topic = input("请输入报告主题（直接回车使用默认）：").strip()
        except (EOFError, KeyboardInterrupt):
            topic = ""
    else:
        topic = ""
    if not topic:
        topic = "AI Agent 在企业客服中的应用"
    
    print(f"\n📝 报告主题：{topic}")
    
    crew = build_crew()
    result = crew.kickoff(inputs={"topic": topic})
    
    print("\n" + "=" * 62)
    print("===== 最终报告 =====")
    print("=" * 62)
    print(result)


if __name__ == "__main__":
    main()
