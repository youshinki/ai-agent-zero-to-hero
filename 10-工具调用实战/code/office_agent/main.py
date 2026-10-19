#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第10篇配套完整项目代码 · main.py
项目入口：整合 RAG知识库 + 工具调用 的办公智能体
==========================================================================

运行:
  cd office_agent
  python main.py

命令: /quit 退出
==========================================================================
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_core import OfficeAgent
from rag_core import RAGCore
from config import USE_MOCK, VERBOSE


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build_demo_docs():
    """创建示例文档"""
    docs_dir = os.path.join(BASE_DIR, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    path = os.path.join(docs_dir, "report.txt")
    if not os.path.exists(path):
        content = """【2024年Q1销售报告】

一、整体业绩
Q1总销售额：1,200,000元，同比增长15%，完成季度目标108%。
其中1月35万，2月40万，3月45万，呈稳步上升趋势。

二、产品线表现
- AI客服系统：销售额60万，占比50%
- 私有知识库：销售额40万，占比33%
- 定制开发：销售额20万，占比17%

三、重点客户
新增3个重点客户，分别是XX银行、YY科技、ZZ制造，
预计全年带来200万以上收入。

四、存在问题
1. 交付周期偏长，平均25天，需压缩到15天
2. 售后响应不及时，客户投诉2次

五、下季度计划
1. 目标销售额150万
2. 推出标准化交付模板
3. 建立7x24小时售后响应机制
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return path


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║        🏢 自动化办公智能体 已启动                        ║
║        《AI Agent 零基础实战》第10篇                     ║
╠══════════════════════════════════════════════════════════╣
║  能力：RAG知识库 + 工具调用(时间/文件/计算) + 反思       ║
║  命令：/quit 退出                                        ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 初始化知识库
    doc_path = build_demo_docs()
    rag = RAGCore()
    rag.init_knowledge_base(doc_path)
    
    agent = OfficeAgent()
    print(f"\n🔧 模式：{'模拟模式（无需API）' if USE_MOCK else '真实API模式'}")
    
    demo_tasks = [
        "现在几点了？",
        "读取 ./docs/report.txt 并告诉我Q1总销售额",
        "计算 1200000 * 1.15",
        "Q1销售报告里产品线占比是多少？",
    ]
    
    if not sys.stdin.isatty():
        print("\n（非交互环境，自动运行演示任务）")
        for task in demo_tasks:
            ans = agent.run(task, rag)
            print(f"\n📤 答案：\n{ans}")
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
        if user_input.lower() in ("/quit", "/exit", "quit", "exit"):
            print("再见！")
            break
        result = agent.run(user_input, rag)
        print(f"\n{'─'*60}\n📤 答案：\n{result}\n{'─'*60}")


if __name__ == "__main__":
    main()
