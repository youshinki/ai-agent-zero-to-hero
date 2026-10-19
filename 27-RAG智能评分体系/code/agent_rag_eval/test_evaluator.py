#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第27篇配套 · test_evaluator.py
验证四维评分体系：
  1. 四维分数计算
  2. 加权总分与五级评级
  3. 自动优化建议
  4. 好/差回答对比（评分能区分质量）
  5. Agent 问答后自动评分

运行: python test_evaluator.py
"""

import os

from knowledge_base.rag_evaluator import evaluator
from knowledge_base.kb_core import kb
from agent_core import agent

UPLOAD_DIR = "knowledge_base/upload_doc"


def main():
    print("=" * 68)
    print("🧪 RAG 智能评分体系测试")
    print("=" * 68)

    # 1. 直接评分：高质量回答
    query = "部署流程分为几个阶段"
    retrieve = "项目部署手册 部署流程分为三个阶段：环境配置、服务启动、日志监控。"
    good_answer = "部署流程分为三个阶段：环境配置、服务启动、日志监控。部署流程完整，均来自私有文档。"
    print("\n[1] 高质量回答评分：")
    result = evaluator.evaluate(query, retrieve, good_answer)
    for k, v in result.items():
        if k != "优化建议":
            print(f"   {k}: {v}")
    for s in result["优化建议"]:
        print(f"   💡 {s}")

    # 2. 低质量回答：残缺 + 重复
    bad_answer = "不知道。\n不知道。\n不知道。\n不知道。"
    print("\n[2] 低质量回答评分：")
    bad = evaluator.evaluate(query, retrieve, bad_answer)
    for k, v in bad.items():
        if k != "优化建议":
            print(f"   {k}: {v}")
    for s in bad["优化建议"]:
        print(f"   💡 {s}")

    print(f"\n   质量区分：好回答{result['综合总分']}分（{result['质量评级']}）"
          f" vs 差回答{bad['综合总分']}分（{bad['质量评级']}）")
    assert result["综合总分"] > bad["综合总分"], "评分应能区分质量"

    # 3. 评级边界
    print("\n[3] 五级评级边界：")
    for score in [95, 85, 75, 65, 50]:
        print(f"   {score}分 → {evaluator.get_grade(score)}")

    # 4. 入库 + Agent 自动评分
    print("\n[4] Agent 问答后自动评分：")
    kb.clear_kb()
    for f in os.listdir(UPLOAD_DIR):
        if f.endswith((".txt", ".md", ".docx")):
            os.remove(os.path.join(UPLOAD_DIR, f))
    docs = {
        "部署手册.txt": "项目部署手册\n部署流程分为三个阶段：环境配置、服务启动、日志监控。\n环境配置需要安装依赖并配置环境变量。",
        "运维规范.txt": "运维规范\n服务器要求：4核CPU、16GB内存、100GB磁盘。\n数据备份每日凌晨2点自动执行。\n故障响应：工作日4小时内响应。",
    }
    for name, content in docs.items():
        with open(os.path.join(UPLOAD_DIR, name), "w", encoding="utf-8") as f:
            f.write(content)
    kb.scan_all_update()

    res = agent.run("部署流程分为几个阶段？", [])
    print(f"   答案：{res['final_answer'][:120].replace(chr(10), ' ')}...")
    q = res.get("quality", {})
    print(f"\n   📊 质量报告：")
    for k, v in q.items():
        if k != "优化建议":
            print(f"      {k}: {v}")
    for s in q.get("优化建议", []):
        print(f"      💡 {s}")
    assert "综合总分" in q, "应返回评分报告"

    # 5. 全部场景
    print("\n[5] 多问题评分对比：")
    for question in ["部署流程分为几个阶段", "服务器配置要求", "数据备份什么时候执行"]:
        r = agent.run(question, [])
        qq = r.get("quality", {})
        print(f"   「{question}」→ {qq.get('综合总分')}分（{qq.get('质量评级')}）")

    print("\n✅ RAG 智能评分测试通过")


if __name__ == "__main__":
    main()
