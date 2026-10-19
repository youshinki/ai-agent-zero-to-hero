#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第60篇配套 · test_agent_eval.py
"""

from agent_eval import (
    EVAL_SET, MockAgent, Evaluator, LLMJudge, human_review, demo,
)


def main():
    print("=" * 66)
    print("🧪 Agent 评估体系测试")
    print("=" * 66)

    print("\n[1] 评测集：")
    assert len(EVAL_SET) == 4
    assert all("expected_tool" in c for c in EVAL_SET)
    print(f"   ✅ {len(EVAL_SET)} 个用例")

    print("\n[2] 指标：")
    ev = Evaluator(MockAgent())
    report = ev.run()
    m = report["metrics"]
    assert m["total"] == 4 and m["passed"] == 4
    assert m["tool_accuracy"] == "100%"
    print(f"   通过率：{m['pass_rate']}｜工具准确率：{m['tool_accuracy']}"
          f"｜平均延迟：{m['avg_latency_ms']}ms")

    print("\n[3] 失败检测：")
    class BadAgent:
        def run(self, q):
            return {"tool": "wrong", "answer": "不知道", "latency_ms": 9999}
    bad = Evaluator(BadAgent()).run()
    assert bad["metrics"]["passed"] == 0
    assert len(bad["failures"]) == 4
    print(f"   坏Agent：通过率{bad['metrics']['pass_rate']}，失败{len(bad['failures'])}个")

    print("\n[4] LLM Judge：")
    s = LLMJudge.score("北京天气", "北京天气：晴 22℃")
    assert s["score"] >= 8
    print(f"   {s['score']}/10 - {s['reason']}")

    print("\n[5] 人工校验：")
    r = human_review(EVAL_SET[0], "pass", "ok")
    assert r["verdict"] == "pass"
    try:
        human_review(EVAL_SET[0], "maybe")
        assert False
    except AssertionError:
        pass

    print("\n[6] 演示：")
    demo()
    print("\n✅ 评估体系测试通过")


if __name__ == "__main__":
    main()
