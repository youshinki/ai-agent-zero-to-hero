#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第60篇配套完整项目代码 · agent_eval.py
Agent 评估体系：自动化评测集、指标设计、人工校验

  1. 评测集（问题/期望答案/期望工具）
  2. 指标：准确率、工具选择准确率、延迟、通过率
  3. LLM Judge（模拟）与人工校验
  4. 评测报告与失败样本
==========================================================================
"""

from typing import (Dict, List)


# ======================================================================
# 一、评测集
# ======================================================================

EVAL_SET = [
    {"id": "e1", "question": "北京天气怎么样", "expected_tool": "get_weather",
     "expected_keywords": ["北京", "天气"], "max_latency_ms": 1000},
    {"id": "e2", "question": "计算 (128+64)*3", "expected_tool": "calculator",
     "expected_keywords": ["576"], "max_latency_ms": 500},
    {"id": "e3", "question": "搜索AI Agent趋势", "expected_tool": "search",
     "expected_keywords": ["搜索"], "max_latency_ms": 1500},
    {"id": "e4", "question": "你好", "expected_tool": None,
     "expected_keywords": [], "max_latency_ms": 300},
]


# ======================================================================
# 二、被测 Agent（模拟）
# ======================================================================

class MockAgent:
    def run(self, question: str) -> Dict:
        import time
        start = time.time()
        if "天气" in question:
            tool, answer = "get_weather", "北京天气：晴 22℃"
        elif "计算" in question:
            tool, answer = "calculator", "计算结果：(128+64)*3 = 576"
        elif "搜索" in question:
            tool, answer = "search", "搜索结果：AI Agent 趋势（3条）"
        else:
            tool, answer = None, "你好，请问有什么可以帮你？"
        latency = int((time.time() - start) * 1000) + 5
        return {"tool": tool, "answer": answer, "latency_ms": latency}


# ======================================================================
# 三、指标
# ======================================================================

def keyword_match(answer: str, keywords: List[str]) -> bool:
    return all(k in answer for k in keywords) if keywords else True


class Evaluator:
    def __init__(self, agent):
        self.agent = agent
        self.results: List[Dict] = []
    
    def run(self) -> Dict:
        self.results = []
        for case in EVAL_SET:
            out = self.agent.run(case["question"])
            tool_ok = out["tool"] == case["expected_tool"]
            keyword_ok = keyword_match(out["answer"], case["expected_keywords"])
            latency_ok = out["latency_ms"] <= case["max_latency_ms"]
            passed = tool_ok and keyword_ok and latency_ok
            self.results.append({
                "id": case["id"], "question": case["question"],
                "tool_ok": tool_ok, "keyword_ok": keyword_ok,
                "latency_ok": latency_ok, "passed": passed,
                "latency_ms": out["latency_ms"],
                "answer": out["answer"],
            })
        return self.report()
    
    def metrics(self) -> Dict:
        n = len(self.results) or 1
        return {
            "total": len(self.results),
            "passed": sum(1 for r in self.results if r["passed"]),
            "pass_rate": f"{sum(1 for r in self.results if r['passed']) / n * 100:.0f}%",
            "tool_accuracy": f"{sum(1 for r in self.results if r['tool_ok']) / n * 100:.0f}%",
            "keyword_accuracy": f"{sum(1 for r in self.results if r['keyword_ok']) / n * 100:.0f}%",
            "latency_pass": f"{sum(1 for r in self.results if r['latency_ok']) / n * 100:.0f}%",
            "avg_latency_ms": round(sum(r["latency_ms"] for r in self.results) / n, 1),
        }
    
    def failures(self) -> List[Dict]:
        return [r for r in self.results if not r["passed"]]
    
    def report(self) -> Dict:
        return {"metrics": self.metrics(), "failures": self.failures()}


# ======================================================================
# 四、LLM Judge（模拟）
# ======================================================================

class LLMJudge:
    """用模型给答案打分（0-10）"""
    
    @staticmethod
    def score(question: str, answer: str) -> Dict:
        score = 5
        if any(k in answer for k in ["天气", "计算", "搜索", "你好"]):
            score += 3
        if len(answer) >= 10:
            score += 2
        return {"score": min(score, 10),
                "reason": "答案与问题相关" if score >= 8 else "答案相关性一般"}


# ======================================================================
# 五、人工校验
# ======================================================================

def human_review(sample: Dict, verdict: str, note: str = "") -> Dict:
    assert verdict in ("pass", "fail")
    return {"id": sample["id"], "verdict": verdict, "note": note}


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("📊 Agent 评估体系演示")
    print("=" * 66)
    ev = Evaluator(MockAgent())
    report = ev.run()
    
    print("\n[1] 指标：")
    for k, v in report["metrics"].items():
        print(f"   {k}: {v}")
    
    print("\n[2] 失败样本：")
    if not report["failures"]:
        print("   （无）")
    for f in report["failures"]:
        print(f"   {f['id']}：{f['question']}（工具:{f['tool_ok']} 关键词:{f['keyword_ok']}）")
    
    print("\n[3] LLM Judge：")
    for case in EVAL_SET[:2]:
        out = MockAgent().run(case["question"])
        s = LLMJudge.score(case["question"], out["answer"])
        print(f"   {case['question']} → {s['score']}/10（{s['reason']}）")
    
    print("\n[4] 人工校验：")
    print(f"   {human_review(EVAL_SET[0], 'pass', '答案准确')}")
    
    assert report["metrics"]["passed"] == 4


if __name__ == "__main__":
    demo()
