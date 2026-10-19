#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第28篇配套 · test_fusion.py
验证"静态知识库 + 动态记忆库"双引擎融合：
  1. 用户自述 → 自动写入偏好档案
  2. 对话 → 自动沉淀长期记忆
  3. 融合上下文包含档案+记忆+知识库
  4. 再次提问时能调用记忆（个性化）
  5. 清空记忆

运行: python test_fusion.py
"""

import os

from knowledge_base.memory_core import memory
from knowledge_base.kb_core import kb
from agent_core import agent, build_fusion_context

UPLOAD_DIR = "knowledge_base/upload_doc"


def main():
    print("=" * 68)
    print("🧪 长期记忆与知识库融合测试")
    print("=" * 68)

    # 清理环境
    memory.clear_memory()
    kb.clear_kb()
    for f in os.listdir(UPLOAD_DIR):
        if f.endswith((".txt", ".md", ".docx")):
            os.remove(os.path.join(UPLOAD_DIR, f))

    # 1. 入库知识库
    docs = {
        "部署手册.txt": "项目部署手册\n部署流程分为三个阶段：环境配置、服务启动、日志监控。\n环境配置需要安装依赖并配置环境变量。",
        "运维规范.txt": "运维规范\n服务器要求：4核CPU、16GB内存、100GB磁盘。\n数据备份每日凌晨2点自动执行。\n故障响应：工作日4小时内响应。",
    }
    for name, content in docs.items():
        with open(os.path.join(UPLOAD_DIR, name), "w", encoding="utf-8") as f:
            f.write(content)
    kb.scan_all_update()
    print(f"[1] 知识库入库：{kb.stats()['documents']} 个文件")

    # 2. 用户自述 → 写入偏好
    print("\n[2] 用户自述（应自动写入偏好档案）：")
    r = agent.run("我是一名AI开发者，喜欢简洁的回答风格，我的部署环境是内网", [])
    print(f"   {r['final_answer'][:80]}")
    print(f"   偏好档案：{memory.store['user_profile']}")
    assert memory.store["user_profile"], "应抽取到用户偏好"

    # 3. 专业问题 → 知识库作答
    print("\n[3] 专业问题（应基于知识库）：")
    r = agent.run("部署流程分为几个阶段？", [])
    print(f"   {r['final_answer'][:150].replace(chr(10), ' ')}...")
    assert "三" in r["final_answer"] or "阶段" in r["final_answer"]

    # 4. 记忆沉淀
    stats = memory.stats()
    print(f"\n[4] 记忆沉淀：{stats}")
    assert stats["chat_memories"] >= 2, "对话应被沉淀"

    # 5. 融合上下文
    print("\n[5] 融合上下文预览：")
    ref_text, _ = kb.build_citation_context("部署流程")
    fusion = build_fusion_context("部署流程", ref_text)
    print(fusion[:400].replace("\n", "\n   "))

    # 6. 个性化提问 → 引用记忆
    print("\n[6] 个性化提问（应记得用户身份/偏好）：")
    r = agent.run("你记得我的身份和偏好吗？", [])
    print(f"   {r['final_answer'][:200].replace(chr(10), ' ')}...")
    profile_text = str(memory.store["user_profile"])
    assert "AI开发者" in profile_text, "应记住身份"

    # 7. 清空记忆
    print("\n[7] 清空记忆：")
    msg = memory.clear_memory()
    print(f"   {msg}  → {memory.stats()}")
    assert memory.stats()["chat_memories"] == 0

    print("\n✅ 长期记忆与知识库融合测试通过")


if __name__ == "__main__":
    main()
