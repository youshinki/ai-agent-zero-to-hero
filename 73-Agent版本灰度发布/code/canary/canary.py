#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第73篇配套完整项目代码 · canary.py
Agent 版本灰度发布：策略A/B测试、流量切分、回归验证

  1. 灰度路由（权重 / 白名单 / 地区）
  2. A/B 指标对比
  3. 自动晋级 / 自动回滚
  4. 回归验证（指标达标才放量）
  5. 发布记录
==========================================================================
"""

import random
from typing import Dict, List


# ======================================================================
# 一、灰度路由
# ======================================================================

class CanaryRouter:
    def __init__(self, v2_weight: float = 0.1, whitelist=None):
        self.v2_weight = v2_weight
        self.whitelist = set(whitelist or [])
        self.routes: Dict[str, int] = {"v1": 0, "v2": 0}
    
    def route(self, user_id: str = "") -> str:
        if user_id in self.whitelist:
            v = "v2"
        elif random.random() < self.v2_weight:
            v = "v2"
        else:
            v = "v1"
        self.routes[v] += 1
        return v
    
    def set_weight(self, weight: float):
        assert 0 <= weight <= 1
        self.v2_weight = weight


# ======================================================================
# 二、A/B 指标
# ======================================================================

class ABTracker:
    def __init__(self):
        self.data: Dict[str, Dict] = {
            "v1": {"requests": 0, "errors": 0, "latency": [],
                   "conversions": 0},
            "v2": {"requests": 0, "errors": 0, "latency": [],
                   "conversions": 0},
        }
    
    def record(self, version: str, latency_ms: float, ok: bool,
               converted: bool = False):
        d = self.data[version]
        d["requests"] += 1
        d["latency"].append(latency_ms)
        if not ok:
            d["errors"] += 1
        if converted:
            d["conversions"] += 1
    
    def metrics(self, version: str) -> Dict:
        d = self.data[version]
        n = d["requests"] or 1
        lat = d["latency"] or [0]
        return {
            "requests": d["requests"],
            "error_rate": round(d["errors"] / n * 100, 2),
            "avg_latency": round(sum(lat) / len(lat), 2),
            "conversion_rate": round(d["conversions"] / n * 100, 2),
        }
    
    def compare(self) -> Dict:
        v1, v2 = self.metrics("v1"), self.metrics("v2")
        return {
            "v1": v1, "v2": v2,
            "error_diff": round(v2["error_rate"] - v1["error_rate"], 2),
            "latency_diff": round(v2["avg_latency"] - v1["avg_latency"], 2),
            "conversion_diff": round(v2["conversion_rate"] - v1["conversion_rate"], 2),
        }


# ======================================================================
# 三、晋级 / 回滚
# ======================================================================

class ReleaseGate:
    """回归验证门槛"""
    
    def __init__(self, max_error_rate: float = 5.0,
                 max_latency_increase: float = 50.0,
                 min_conversion_drop: float = -2.0):
        self.max_error_rate = max_error_rate
        self.max_latency_increase = max_latency_increase
        self.min_conversion_drop = min_conversion_drop
    
    def evaluate(self, compare: Dict) -> Dict:
        v1, v2 = compare["v1"], compare["v2"]
        reasons = []
        
        if v2["error_rate"] > self.max_error_rate:
            reasons.append(f"v2错误率过高：{v2['error_rate']}%")
        if v1["avg_latency"] and compare["latency_diff"] > self.max_latency_increase:
            reasons.append(f"v2延迟增加：{compare['latency_diff']}ms")
        if compare["conversion_diff"] < self.min_conversion_drop:
            reasons.append(f"v2转化下降：{compare['conversion_diff']}%")
        
        return {
            "pass": not reasons,
            "decision": "promote" if not reasons else "rollback",
            "reasons": reasons,
        }


class ReleaseManager:
    """按阶段放量：1% → 10% → 50% → 100%"""
    STAGES = [0.01, 0.1, 0.5, 1.0]
    
    def __init__(self, tracker: ABTracker, gate: ReleaseGate,
                 router: CanaryRouter):
        self.tracker = tracker
        self.gate = gate
        self.router = router
        self.stage_idx = 0
        self.history: List[Dict] = []
    
    def current_weight(self) -> float:
        return self.STAGES[self.stage_idx]
    
    def step(self) -> Dict:
        compare = self.tracker.compare()
        verdict = self.gate.evaluate(compare)
        record = {"stage": self.stage_idx,
                  "weight": self.current_weight(),
                  "compare": compare, "verdict": verdict}
        self.history.append(record)
        
        if not verdict["pass"]:
            self.router.set_weight(0.0)
            record["action"] = "rollback"
            return record
        
        if self.stage_idx < len(self.STAGES) - 1:
            self.stage_idx += 1
            self.router.set_weight(self.current_weight())
            record["weight"] = self.current_weight()
            record["action"] = "promote"
        else:
            record["action"] = "full_release"
        return record


def demo():
    print("=" * 66)
    print("🚦 版本灰度发布演示")
    print("=" * 66)
    
    random.seed(3)
    router = CanaryRouter(v2_weight=0.1, whitelist=["beta_user"])
    tracker = ABTracker()
    
    print("\n[1] 灰度路由：")
    for uid in ["u1", "beta_user", "u3", "u4", "beta_user"]:
        v = router.route(uid)
        print(f"   {uid} → {v}")
    
    print("\n[2] A/B 数据采集：")
    for _ in range(100):
        tracker.record("v1", random.uniform(80, 120), random.random() > 0.02,
                       converted=random.random() < 0.2)
        tracker.record("v2", random.uniform(85, 130), random.random() > 0.01,
                       converted=random.random() < 0.22)
    cmp = tracker.compare()
    for k in ["error_diff", "latency_diff", "conversion_diff"]:
        print(f"   {k}: {cmp[k]}")
    
    print("\n[3] 回归判定：")
    gate = ReleaseGate()
    print(f"   {gate.evaluate(cmp)}")
    
    print("\n[4] 分阶段放量：")
    mgr = ReleaseManager(tracker, gate, router)
    for _ in range(5):
        rec = mgr.step()
        print(f"   阶段{rec['stage']}（权重{rec['weight']}）→ {rec['action']}")
        if rec["action"] in ("rollback", "full_release"):
            break


if __name__ == "__main__":
    demo()
