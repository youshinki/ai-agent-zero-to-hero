#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第68篇配套完整项目代码 · observability.py
Agent 链路可观测：日志埋点、调用追踪、指标告警、链路定位

  1. Trace/Span 调用链
  2. 结构化日志与关联
  3. 指标聚合（QPS/延迟/错误率/Token）
  4. 告警规则
  5. 链路定位（按 trace_id 回放）
==========================================================================
"""

import statistics
import time
from typing import Dict, List, Optional


# ======================================================================
# 一、调用链
# ======================================================================

class Span:
    def __init__(self, name: str, trace_id: str, parent_id: str = ""):
        self.name = name
        self.trace_id = trace_id
        self.parent_id = parent_id
        self.start = time.time()
        self.end: Optional[float] = None
        self.status = "ok"
        self.attributes: Dict = {}
    
    def finish(self, status: str = "ok", **attrs):
        self.end = time.time()
        self.status = status
        self.attributes.update(attrs)
        return self
    
    @property
    def duration_ms(self) -> float:
        return round(((self.end or time.time()) - self.start) * 1000, 2)


class Tracer:
    def __init__(self):
        self.spans: List[Span] = []
    
    def start_span(self, name: str, trace_id: str,
                   parent_id: str = "") -> Span:
        span = Span(name, trace_id, parent_id)
        self.spans.append(span)
        return span
    
    def trace(self, trace_id: str) -> List[Span]:
        return [s for s in self.spans if s.trace_id == trace_id]


# ======================================================================
# 二、日志
# ======================================================================

class StructuredLogger:
    def __init__(self):
        self.logs: List[Dict] = []
    
    def log(self, level: str, trace_id: str, message: str, **fields):
        entry = {"ts": round(time.time(), 3), "level": level,
                 "trace_id": trace_id, "message": message, **fields}
        self.logs.append(entry)
        return entry
    
    def by_trace(self, trace_id: str) -> List[Dict]:
        return [l for l in self.logs if l["trace_id"] == trace_id]


# ======================================================================
# 三、指标
# ======================================================================

class Metrics:
    def __init__(self):
        self.requests: List[Dict] = []
    
    def record(self, trace_id: str, latency_ms: float, ok: bool,
               tokens: int = 0, model: str = ""):
        self.requests.append({"trace_id": trace_id, "latency_ms": latency_ms,
                              "ok": ok, "tokens": tokens, "model": model})
    
    def summary(self) -> Dict:
        if not self.requests:
            return {"count": 0}
        latencies = [r["latency_ms"] for r in self.requests]
        errors = sum(1 for r in self.requests if not r["ok"])
        return {
            "count": len(self.requests),
            "error_rate": f"{errors / len(self.requests) * 100:.1f}%",
            "avg_latency_ms": round(statistics.mean(latencies), 2),
            "p95_latency_ms": round(self._p95(latencies), 2),
            "total_tokens": sum(r["tokens"] for r in self.requests),
        }
    
    @staticmethod
    def _p95(values: List[float]) -> float:
        if not values:
            return 0.0
        s = sorted(values)
        idx = min(int(len(s) * 0.95), len(s) - 1)
        return s[idx]


# ======================================================================
# 四、告警
# ======================================================================

class AlertRules:
    RULES = [
        {"name": "error_rate", "metric": "error_rate", "op": ">", "value": 5,
         "level": "critical", "desc": "错误率超过5%"},
        {"name": "p95_latency", "metric": "p95_latency_ms", "op": ">",
         "value": 1000, "level": "warning", "desc": "P95延迟超过1s"},
        {"name": "token_spike", "metric": "total_tokens", "op": ">",
         "value": 10000, "level": "warning", "desc": "Token消耗异常"},
    ]
    
    @classmethod
    def evaluate(cls, summary: Dict) -> List[Dict]:
        alerts = []
        for rule in cls.RULES:
            v = summary.get(rule["metric"])
            if isinstance(v, str):
                try:
                    v = float(v.rstrip("%"))
                except ValueError:
                    continue
            if v is None:
                continue
            if rule["op"] == ">" and v > rule["value"]:
                alerts.append({"rule": rule["name"], "level": rule["level"],
                               "desc": rule["desc"], "value": v})
        return alerts


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("🔭 Agent 链路可观测演示")
    print("=" * 66)
    
    tracer, logger, metrics = Tracer(), StructuredLogger(), Metrics()
    
    trace_id = "trace-001"
    logger.log("info", trace_id, "请求开始", user="alice")
    
    root = tracer.start_span("agent.run", trace_id)
    plan = tracer.start_span("plan", trace_id, "agent.run")
    time.sleep(0.002)
    plan.finish(step_count=3)
    
    tool = tracer.start_span("tool.search", trace_id, "agent.run")
    time.sleep(0.003)
    tool.finish(status="ok", tool="search")
    
    llm = tracer.start_span("llm.chat", trace_id, "agent.run")
    time.sleep(0.004)
    llm.finish(model="deepseek-chat", tokens_in=120, tokens_out=80)
    
    root.finish()
    logger.log("info", trace_id, "请求完成", latency_ms=root.duration_ms)
    metrics.record(trace_id, root.duration_ms, True, 200, "deepseek-chat")
    
    print(f"\n[1] 调用链（trace={trace_id}）：")
    for s in tracer.trace(trace_id):
        print(f"   {s.name:16s} {s.duration_ms:7.2f}ms {s.status}")
    
    print(f"\n[2] 日志：")
    for l in logger.by_trace(trace_id):
        print(f"   [{l['level']}] {l['message']} {l.get('user','')}")
    
    print(f"\n[3] 指标：")
    print(f"   {metrics.summary()}")
    
    print(f"\n[4] 告警：")
    for m in [{"error_rate": "8%", "p95_latency_ms": 1500, "total_tokens": 20000},
              {"error_rate": "1%", "p95_latency_ms": 300, "total_tokens": 500}]:
        print(f"   {m} → {AlertRules.evaluate(m)}")


if __name__ == "__main__":
    demo()
