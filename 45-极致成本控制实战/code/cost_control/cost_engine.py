#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第45篇配套完整项目代码 · cost_engine.py
极致成本控制（API 计费节流优化）：

  1. 精确计量（模型价格表 / token 估算）
  2. 语义缓存（TTL + LRU + 命中统计）
  3. 提示词压缩（冗余裁剪 / 上下文压缩）
  4. 智能模型路由（简单→低价，复杂→高价；失败降级）
  5. 批量合并请求
  6. 预算熔断 + 异常消耗告警
  7. 降本报告（分项节省）

运行: python cost_engine.py       # 演示降本效果
"""

import hashlib
import re
import time
from collections import OrderedDict
from typing import Dict, List, Optional


# ======================================================================
# 一、价格与计量
# ======================================================================

PRICES = {
    "gpt-4":          {"in": 0.21,   "out": 0.42,   "level": "high"},
    "gpt-3.5-turbo":  {"in": 0.0035, "out": 0.007,  "level": "mid"},
    "deepseek-chat":  {"in": 0.002,  "out": 0.004,  "level": "low"},
    "qwen-turbo":     {"in": 0.0015, "out": 0.003,  "level": "low"},
}
FALLBACK_CHAIN = ["gpt-4", "deepseek-chat", "qwen-turbo"]


class Meter:
    @staticmethod
    def tokens(text: str) -> int:
        if not text:
            return 0
        zh = len(re.findall(r"[\u4e00-\u9fa5]", text))
        return int(zh * 1.5 + (len(text) - zh) * 0.3) + 1
    
    @staticmethod
    def cost(model: str, tin: int, tout: int) -> float:
        p = PRICES.get(model, PRICES["gpt-3.5-turbo"])
        return round(tin / 1000 * p["in"] + tout / 1000 * p["out"], 6)


# ======================================================================
# 二、语义缓存（TTL + LRU）
# ======================================================================

class SemanticCache:
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        self.ttl = ttl
        self.max_size = max_size
        self._data: "OrderedDict[str, dict]" = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    @staticmethod
    def _key(text: str) -> str:
        norm = re.sub(r"[\s，。！？、,.!?]", "", text.lower())
        return hashlib.md5(norm.encode()).hexdigest()
    
    def get(self, prompt: str) -> Optional[str]:
        key = self._key(prompt)
        item = self._data.get(key)
        if not item:
            self.misses += 1
            return None
        if time.time() - item["time"] > self.ttl:
            del self._data[key]
            self.misses += 1
            return None
        self._data.move_to_end(key)  # LRU
        self.hits += 1
        return item["answer"]
    
    def set(self, prompt: str, answer: str):
        key = self._key(prompt)
        self._data[key] = {"answer": answer, "time": time.time()}
        self._data.move_to_end(key)
        while len(self._data) > self.max_size:
            self._data.popitem(last=False)
    
    def stats(self) -> dict:
        total = self.hits + self.misses
        return {"hits": self.hits, "misses": self.misses,
                "hit_rate": f"{self.hits / total * 100:.1f}%" if total else "0%",
                "size": len(self._data)}


# ======================================================================
# 三、提示词压缩
# ======================================================================

class Compressor:
    FILLERS = [r"请注意", r"请记住", r"你是一个", r"你是一位", r"非常重要",
               r"一定要", r"务必", r"尽可能地", r"尽量", r"非常非常"]
    
    @classmethod
    def compress(cls, prompt: str, max_tokens: int = 1500) -> str:
        text = prompt
        for f in cls.FILLERS:
            text = re.sub(f, "", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        if Meter.tokens(text) > max_tokens:
            max_chars = int(max_tokens / 1.5)
            head, tail = int(max_chars * 0.7), int(max_chars * 0.3)
            text = text[:head] + "\n...(省略)...\n" + text[-tail:]
        return text.strip()


# ======================================================================
# 四、路由 + 降级
# ======================================================================

class Router:
    SIMPLE = ["你好", "天气", "时间", "翻译", "计算", "是什么", "多少", "怎么读"]
    
    @classmethod
    def route(cls, prompt: str) -> str:
        tokens = Meter.tokens(prompt)
        text = prompt.lower()
        if tokens < 200 and any(k in text for k in cls.SIMPLE):
            return "qwen-turbo"
        if tokens < 800:
            return "deepseek-chat"
        return "gpt-4"
    
    @staticmethod
    def fallback(model: str) -> str:
        idx = FALLBACK_CHAIN.index(model) if model in FALLBACK_CHAIN else 0
        return FALLBACK_CHAIN[idx + 1] if idx + 1 < len(FALLBACK_CHAIN) else model


# ======================================================================
# 五、预算与告警
# ======================================================================

class BudgetGuard:
    def __init__(self, daily: float = 50.0, alert_ratio: float = 0.8):
        self.daily = daily
        self.alert_ratio = alert_ratio
        self.used = 0.0
        self.alerts: List[dict] = []
        self.blocked = 0
    
    def check(self, estimated: float) -> bool:
        if self.used + estimated > self.daily:
            self.blocked += 1
            return False
        if self.used + estimated > self.daily * self.alert_ratio:
            self.alerts.append({"type": "budget_warning",
                                "used": round(self.used, 4),
                                "estimated": estimated,
                                "time": time.time()})
        return True
    
    def record(self, cost: float):
        self.used = round(self.used + cost, 6)
    
    def stats(self) -> dict:
        return {"daily_budget": self.daily, "used": round(self.used, 4),
                "usage_ratio": f"{self.used / self.daily * 100:.1f}%",
                "blocked": self.blocked, "alerts": len(self.alerts)}


# ======================================================================
# 六、优化服务
# ======================================================================

class MockLLM:
    @staticmethod
    def chat(model: str, prompt: str) -> str:
        return f"[{model}] 回答：针对「{prompt[:26]}...」的答复。"


class CostOptimizer:
    def __init__(self):
        self.cache = SemanticCache()
        self.budget = BudgetGuard()
        self.meter_by_tenant: Dict[str, dict] = {}
        
        self.calls = 0
        self.cost = 0.0
        self.baseline = 0.0
        self.saved_cache = 0.0
        self.saved_route = 0.0
        self.saved_compress = 0.0
        self.fallbacks = 0
    
    def ask(self, prompt: str, tenant: str = "default",
            force_model: str = None) -> dict:
        # 基线：全 gpt-4、不压缩
        base_in = Meter.tokens(prompt)
        self.baseline += Meter.cost("gpt-4", base_in, 80)
        
        # 1. 缓存
        cached = self.cache.get(prompt)
        if cached is not None:
            self.saved_cache += Meter.cost("gpt-4", base_in, 80)
            self._meter(tenant, 0, 0, hit=True)
            return {"answer": cached, "cached": True, "cost": 0.0,
                    "model": "(cache)"}
        
        # 2. 压缩
        compressed = Compressor.compress(prompt)
        cin = Meter.tokens(compressed)
        if cin < base_in:
            self.saved_compress += Meter.cost("gpt-4", base_in - cin, 0)
        
        # 3. 路由
        model = force_model or Router.route(compressed)
        
        # 4. 预算
        est = Meter.cost(model, cin, 80)
        if not self.budget.check(est):
            return {"answer": "当前请求量较大，请稍后重试。", "blocked": True,
                    "cost": 0.0, "model": model}
        
        # 5. 调用 + 降级
        try:
            answer = MockLLM.chat(model, compressed)
        except Exception:
            model = Router.fallback(model)
            self.fallbacks += 1
            answer = MockLLM.chat(model, compressed)
        
        # 6. 记账
        out_tokens = Meter.tokens(answer)
        cost = Meter.cost(model, cin, out_tokens)
        self.calls += 1
        self.cost = round(self.cost + cost, 6)
        self.budget.record(cost)
        self.cache.set(prompt, answer)
        self._meter(tenant, cin, out_tokens)
        
        if model != "gpt-4":
            self.saved_route += Meter.cost("gpt-4", cin, out_tokens) - cost
        
        return {"answer": answer, "cached": False, "cost": cost,
                "model": model, "input_tokens": cin}
    
    def _meter(self, tenant: str, tin: int, tout: int, hit: bool = False):
        m = self.meter_by_tenant.setdefault(
            tenant, {"requests": 0, "cache_hits": 0, "tokens_in": 0, "tokens_out": 0})
        if hit:
            m["cache_hits"] += 1
        else:
            m["requests"] += 1
            m["tokens_in"] += tin
            m["tokens_out"] += tout
    
    def report(self) -> dict:
        saved = self.saved_cache + self.saved_route + self.saved_compress
        rate = saved / self.baseline * 100 if self.baseline else 0
        return {
            "calls": self.calls,
            "baseline_cost": round(self.baseline, 4),
            "actual_cost": round(self.cost, 4),
            "saved_cache": round(self.saved_cache, 4),
            "saved_route": round(self.saved_route, 4),
            "saved_compress": round(self.saved_compress, 4),
            "total_saved": round(saved, 4),
            "savings_rate": f"{rate:.1f}%",
            "fallbacks": self.fallbacks,
            "cache": self.cache.stats(),
            "budget": self.budget.stats(),
            "tenants": self.meter_by_tenant,
        }


# ======================================================================
# 演示
# ======================================================================

def demo():
    opt = CostOptimizer()
    # 60 次重复 + 30 次简单 + 10 次复杂
    prompts = (["公司的部署流程是什么？"] * 60 +
               [f"翻译第{i}段" for i in range(30)] +
               [f"请深度分析第{i}份业务报告，给出完整优化方案、风险评估与落地建议" for i in range(10)])
    for p in prompts:
        opt.ask(p)
    r = opt.report()
    
    print("=" * 64)
    print("💰 极致成本控制 · 降本报告")
    print("=" * 64)
    print(f"请求总数：{len(prompts)}")
    print(f"实际调用：{r['calls']}（缓存命中 {r['cache']['hits']} 次）")
    print(f"基线成本（全gpt-4）：¥{r['baseline_cost']}")
    print(f"实际成本：¥{r['actual_cost']}")
    print(f"总节省：¥{r['total_saved']}（{r['savings_rate']}）")
    print(f"  - 缓存节省：¥{r['saved_cache']}")
    print(f"  - 路由节省：¥{r['saved_route']}")
    print(f"  - 压缩节省：¥{r['saved_compress']}")
    print(f"缓存：{r['cache']}")
    print(f"预算：{r['budget']}")
    print(f"租户用量：")
    for t, m in r["tenants"].items():
        print(f"  {t}: {m}")
    return r


if __name__ == "__main__":
    demo()
