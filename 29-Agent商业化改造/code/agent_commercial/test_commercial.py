#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第29篇配套 · test_commercial.py
对比"开发模式原始输出"与"商业模式成品输出"，
验证四层净化：去开发信息 / 标准排版 / 异常兜底 / 产品级输出。

运行: python test_commercial.py
"""

import os

from knowledge_base.kb_core import kb
from knowledge_base.memory_core import memory
import commercial_wrapper as cw
from agent_core import agent

UPLOAD_DIR = "knowledge_base/upload_doc"


def main():
    print("=" * 68)
    print("🧪 Agent 商业化改造测试")
    print("=" * 68)

    # 准备知识库
    memory.clear_memory()
    kb.clear_kb()
    for f in os.listdir(UPLOAD_DIR):
        if f.endswith((".txt", ".md", ".docx")):
            os.remove(os.path.join(UPLOAD_DIR, f))
    docs = {
        "部署手册.txt": "项目部署手册\n部署流程分为三个阶段：环境配置、服务启动、日志监控。",
        "运维规范.txt": "运维规范\n服务器要求：4核CPU、16GB内存、100GB磁盘。\n数据备份每日凌晨2点自动执行。",
    }
    for name, content in docs.items():
        with open(os.path.join(UPLOAD_DIR, name), "w", encoding="utf-8") as f:
            f.write(content)
    kb.scan_all_update()

    question = "部署流程分为几个阶段？"

    # 1. 开发模式原始输出（含调试信息）
    cw.COMMERCIAL_MODE = False
    raw_result = agent.run(question, [])
    raw = raw_result["final_answer"]
    print("\n[1] 开发模式原始输出（含技术噪声）：")
    print("-" * 68)
    print(raw)
    print("-" * 68)

    # 2. 开启商业模式
    cw.COMMERCIAL_MODE = True
    # 需要重新实例化 wrapper 以使用新开关（wrapper 内每次调用读取全局开关）
    wrapper = cw.CommercialAgentWrapper()
    commercial = wrapper.safe_answer(question)
    print("\n[2] 商业模式成品输出（干净）：")
    print("-" * 68)
    print(commercial["answer"])
    print("-" * 68)

    # 3. 校验净化效果
    answer = commercial["answer"]
    noise = ["片段", "综合匹配分", "来源文档", "【高精度知识库检索结果】", "核心内容", "[引用"]
    print("\n[3] 净化校验：")
    for n in noise:
        present = n in answer
        print(f"   {'❌ 残留' if present else '✅ 已清除'}：{n}")
        assert not present, f"商业输出不应包含 {n}"
    assert commercial["success"] is True

    # 4. 输出排版（多行分段）
    print("\n[4] 排版检查：")
    lines = [l for l in answer.split("\n") if l.strip()]
    print(f"   行数：{len(lines)}（按句分段）")
    assert len(lines) >= 1

    # 5. 异常兜底
    print("\n[5] 异常兜底测试：")
    wrapper2 = cw.CommercialAgentWrapper()
    original_run = wrapper2.agent.run
    wrapper2.agent.run = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("模拟内部错误"))
    err = wrapper2.safe_answer("随便问点什么")
    print(f"   错误输出：{err['answer']}")
    assert err["success"] is False and "模拟" not in err["answer"], "不应暴露内部错误细节"

    # 6. 空输出兜底
    wrapper2.agent.run = lambda *a, **k: {"final_answer": ""}
    empty = wrapper2.safe_answer("问点什么")
    print(f"   空输出兜底：{empty['answer']}")
    assert "暂未查询到" in empty["answer"]

    # 恢复
    wrapper2.agent.run = original_run

    print("\n✅ 商业化改造测试全部通过")


if __name__ == "__main__":
    main()
