#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第26篇配套 · test_citation.py
验证溯源引用闭环：
  1. 检索结果绑定文档名 / 片段索引 / 匹配分数
  2. 生成带【引用N】的回答
  3. 自动汇总去重参考文献
  4. 无相关内容时如实拒答

运行: python test_citation.py
"""

import os

from knowledge_base.kb_core import kb
from agent_core import agent, RAG_SYSTEM_PROMPT

UPLOAD_DIR = "knowledge_base/upload_doc"

DOCS = {
    "部署手册.txt": """项目部署手册
部署流程分为三个阶段：环境配置、服务启动、日志监控。
环境配置需要安装依赖并配置环境变量，确保端口8000未被占用。
服务启动后可通过定时任务实现全自动巡检。
""",
    "运维规范.txt": """运维规范
服务器要求：4核CPU、16GB内存、100GB磁盘。
数据备份每日凌晨2点自动执行。
故障响应：工作日4小时内响应。
""",
}


def main():
    print("=" * 68)
    print("🧪 RAG 溯源引用机制测试")
    print("=" * 68)
    print("\n系统提示词（引用规则）：")
    print(RAG_SYSTEM_PROMPT)

    # 1. 入库
    kb.clear_kb()
    for f in os.listdir(UPLOAD_DIR):
        if f.endswith((".txt", ".md", ".docx")):
            os.remove(os.path.join(UPLOAD_DIR, f))
    for name, content in DOCS.items():
        with open(os.path.join(UPLOAD_DIR, name), "w", encoding="utf-8") as f:
            f.write(content)
    log = kb.scan_all_update()
    print(f"\n[1] 入库：{len(log)}个文件")
    for x in log:
        print(f"   {x['status']} | {x['message']}")

    # 2. 结构化检索（带溯源）
    print("\n[2] 结构化溯源检索：")
    hits = kb.search("部署流程分为几个阶段", top_k=3)
    for h in hits:
        print(f"   [引用{h['ref_id']}] {h['source']} 综合{h['total_score']} | {h['content'][:40]}...")
    assert hits and all("ref_id" in h for h in hits), "检索结果应带 ref_id"

    # 3. 构建带引用上下文
    print("\n[3] 带引用上下文：")
    ref_text, ref_map = kb.build_citation_context("部署流程分为几个阶段")
    print(ref_text)
    print(f"   ref_map: { {k: v['source'] for k, v in ref_map.items()} }")

    # 4. Agent 引用式回答
    print("\n[4] Agent 溯源问答：")
    res = agent.run("部署流程分为几个阶段？", [])
    print(res["final_answer"])
    assert "【引用" in res["final_answer"], "回答应包含引用标记"
    assert "【参考文献】" in res["final_answer"], "回答应包含参考文献"

    # 5. 参考文献去重
    print("\n[5] 参考文献去重：")
    summary = kb.get_ref_summary(ref_text)
    print(summary)
    assert summary.count("1.") >= 1

    # 6. 无相关内容拒答
    print("\n[6] 无相关内容拒答：")
    res2 = agent.run("公司的股票代码是多少？", [])
    print(f"   {res2['final_answer']}")
    assert "无" in res2["final_answer"] or "暂无" in res2["final_answer"], "应如实拒答"

    print("\n✅ 溯源引用机制测试通过")


if __name__ == "__main__":
    main()
