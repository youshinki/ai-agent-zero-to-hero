#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第9篇配套完整项目代码 · main.py
项目入口：初始化RAG知识库 + 私有文档问答Agent
==========================================================================

运行方式:
  cd rag_agent
  python main.py

交互命令:
  /quit  退出
  /stats 查看知识库状态
==========================================================================
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_core import BaseAgent
from rag_core import RAGCore
from config import USE_MOCK


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build_demo_docs():
    """若示例文档不存在，自动创建"""
    docs_dir = os.path.join(BASE_DIR, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    demo_path = os.path.join(docs_dir, "test.txt")
    if not os.path.exists(demo_path):
        content = """【公司产品手册 · AI智能客服系统】

一、产品概述
AI智能客服系统是一套基于RAG架构的私有知识库问答解决方案，支持多轮对话、
知识库问答和工具调用。系统采用私有化部署方式，数据不出企业内网。

二、核心功能
1. 多轮对话：支持上下文记忆，可进行连续多轮交流。
2. 知识库问答：导入企业文档后，可基于资料精准回答，显著降低幻觉。
3. 工具调用：支持查天气、计算器、文件读取等工具。
4. 溯源引用：每个答案均可标注来源文档，实现有据可查。

三、部署要求
- 服务器：4核CPU、16GB内存、100GB磁盘
- 系统：Linux CentOS 7+ 或 Ubuntu 20.04+
- 依赖：Python 3.10+、Docker 20.10+
- 网络：支持内网部署，无需外网

四、收费方案
- 基础版：15000元，知识库容量10万条，支持10个用户
- 标准版：30000元，知识库容量50万条，支持50个用户
- 企业版：80000元起，知识库不限量，支持私有化定制

五、技术支持
- 工作日4小时内响应，非工作日12小时内响应
- 提供7天免费维护，交付后30天技术支持
- 联系方式：support@example.com

六、适用行业
已落地金融、医疗、制造三个行业。其中金融行业客户问答准确率从78%提升至96%。
"""
        with open(demo_path, "w", encoding="utf-8") as f:
            f.write(content)
    return demo_path


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║        📚 私有文档问答 Agent 已启动                      ║
║        《AI Agent 零基础实战》第9篇                      ║
╠══════════════════════════════════════════════════════════╣
║  RAG五步法：加载→分块→向量化→检索→增强生成             ║
║  命令：/quit 退出   /stats 知识库状态                    ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 1. 初始化RAG知识库
    doc_path = build_demo_docs()
    rag = RAGCore()
    rag.init_knowledge_base(doc_path)
    
    # 2. 初始化智能体
    agent = BaseAgent()
    print(f"\n🔧 模式：{'模拟模式（无需API）' if USE_MOCK else '真实API模式'}")
    
    # 演示问题
    demo_questions = [
        "AI智能客服系统有哪些核心功能？",
        "这个系统部署需要什么服务器配置？",
        "企业版多少钱？",
        "支持哪些行业？",
    ]
    
    interactive = sys.stdin.isatty()
    
    if not interactive:
        print("\n（非交互环境，自动运行演示问答）")
        for q in demo_questions:
            answer = agent.run(q, rag)
            print(f"\n📤 答案：\n{answer}")
        print("\n✅ 演示完成。")
        return
    
    while True:
        try:
            user_input = input("\n❓ 请输入问题（/quit 退出）：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        
        if not user_input:
            continue
        if user_input.lower() in ("/quit", "/exit", "quit", "exit"):
            print("感谢使用，再见！")
            break
        if user_input.lower() == "/stats":
            s = rag.stats()
            print(f"\n📊 知识库状态：文档{s['documents']}篇 / 块{s['chunks']}个 / 向量{s['embedding_dim']}维")
            continue
        
        result = agent.run(user_input, rag)
        print(f"\n{'─'*60}")
        print(f"📤 答案：\n{result}")
        print(f"{'─'*60}")


if __name__ == "__main__":
    main()
