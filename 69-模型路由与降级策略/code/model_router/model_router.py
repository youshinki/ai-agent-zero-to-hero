#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第69篇配套完整项目代码 · model_router.py
模型路由与降级：多模型智能分发、超时熔断、主备自动切换

  1. 多模型健康度与路由策略（成本/质量/延迟）
  2. 超时控制
  3. 熔断器
  4. 主备自动切换（failover）
  5. 路由统计
==========================================================================
"""

import random
import time
from typing import Dict, List, Optional


# ======================================================================
# 一、模型池
# ======================================================================

MODELS = {
    "gpt-4": {"quality": 10, "cost": 10, "latency": 8, "role": "primary"},
    "deepseek-chat": {"quality": 8, "cost": 2, "latency": 3, "role": "balanced"},
    "qwen-turbo": {"quality": 6, "cost": 1, "latency": 1, "role": "cheap"},
}

FAILOVER_CHAIN = ["gpt-4", "deepseek-chat", "qwen-turbo"]


# ======================================================================
# 二、路由器
# ======================================================================

class ModelRouter:
    def __init__(self, strategy: str = "balanced"):
        self.strategy = strategy  # cost / quality / latency / balanced
        self.health: Dict[str, bool] = {m: True for m in MODELS}
        self.stats: Dict[str, int] = {m: 0 for m in MODELS}
    
    def score(self, model: str) -> float:
        info = MODELS[model]
        q, c, l = info["quality"], info["cost"], info["latency"]
        if self.strategy == "quality":
            return q
        if self.strategy == "cost":
            return 10 - c
        if self.strategy == "latency":
            return 10 - l
        # balanced：质量优先 + 成本/延迟折扣
        return q * 0.6 + (10 - c) * 0.2 + (10 - l) * 0.2
    
    def pick(self, complexity: str = "medium") -> str:
        candidates = [m for m, ok in self.health.items() if ok]
        if not candidates:
            return "qwen-turbo"
        # 简单任务优先便宜模型
        if complexity == "low":
            cheap = [m for m in candidates if MODELS[m]["role"] == "cheap"]
            if cheap:
                return cheap[0]
        return max(candidates, key=self.score)
    
    def failover(self, failed: str) -> Optional[str]:
        self.health[failed] = False
        idx = FAILOVER_CHAIN.index(failed) if failed in FAILOVER_CHAIN else -1
        for m in FAILOVER_CHAIN[idx + 1:]:
            if self.health.get(m, False):
                return m
        # 全部失败，尝试恢复最便宜的
        for m in FAILOVER_CHAIN:
            if self.health.get(m):
                return m
        return None
    
    def mark_healthy(self, model: str):
        self.health[model] = True


# ======================================================================
# 三、带熔断的调用
# ======================================================================

class CircuitBreaker:
    def __init__(self, threshold: int = 2, recovery: float = 0.2):
        self.threshold = threshold
        self.recovery = recovery
        self.failures = 0
        self.open = False
        self.opened_at = 0.0
    
    def allow(self) -> bool:
        if self.open and time.time() - self.opened_at >= self.recovery:
            self.open = False
            self.failures = 0
        return not self.open
    
    def success(self):
        self.failures = 0
        self.open = False
    
    def failure(self):
        self.failures += 1
        if self.failures >= self.threshold:
            self.open = True
            self.opened_at = time.time()


class RobustRouter:
    def __init__(self, strategy: str = "balanced", timeout: float = 0.5):
        self.router = ModelRouter(strategy)
        self.breakers: Dict[str, CircuitBreaker] = {
            m: CircuitBreaker() for m in MODELS}
        self.timeout = timeout
        self.log: List[Dict] = []
    
    def call(self, prompt: str, complexity: str = "medium") -> Dict:
        model = self.router.pick(complexity)
        tried = []
        
        while model:
            tried.append(model)
            cb = self.breakers[model]
            if not cb.allow():
                self.log.append({"model": model, "ok": False,
                                 "reason": "熔断中"})
                model = self.router.failover(model)
                continue
            
            try:
                result = self._invoke(model, prompt)
                cb.success()
                self.router.mark_healthy(model)
                self.router.stats[model] += 1
                self.log.append({"model": model, "ok": True})
                return {"ok": True, "model": model, "result": result,
                        "tried": tried}
            except Exception as e:
                cb.failure()
                self.log.append({"model": model, "ok": False,
                                 "reason": str(e)})
                model = self.router.failover(model)
        
        return {"ok": False, "error": "所有模型不可用", "tried": tried}
    
    def _invoke(self, model: str, prompt: str) -> str:
        # 模拟：gpt-4 偶发超时/失败
        if model == "gpt-4" and random.random() < 0.5:
            raise TimeoutError("模型超时")
        return f"[{model}] 回答：{prompt[:20]}"


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("🔀 模型路由与降级演示")
    print("=" * 66)
    
    print("\n[1] 不同策略选模型：")
    for strategy in ["quality", "cost", "latency", "balanced"]:
        r = ModelRouter(strategy)
        print(f"   {strategy:8s} → {r.pick()}")
    
    print("\n[2] 复杂度路由：")
    r = ModelRouter("balanced")
    for c in ["low", "medium", "high"]:
        print(f"   {c:6s} → {r.pick(c)}")
    
    print("\n[3] 主备切换：")
    r = ModelRouter()
    print(f"   gpt-4 失败 → {r.failover('gpt-4')}")
    print(f"   deepseek 失败 → {r.failover('deepseek-chat')}")
    
    print("\n[4] 带熔断的调用（gpt-4 50%失败）：")
    rr = RobustRouter()
    random.seed(42)
    for i in range(3):
        out = rr.call(f"问题{i}", "high")
        print(f"   第{i+1}次：{out['model'] if out['ok'] else out.get('error')}"
              f"，尝试{out['tried']}")


if __name__ == "__main__":
    demo()
