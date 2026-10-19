#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第31篇配套完整项目代码 · commercial_service.py
成本优化后的商用服务层：
  路由 → 压缩 → 缓存 → 预算检查 → 调用 → 记账
==========================================================================
"""

from typing import Dict

from cost_optimizer import (
    TokenCounter, PromptCompressor, SemanticCache,
    ModelRouter, BatchProcessor, BudgetGuard,
)
from config import BATCH_SIZE


class MockLLM:
    """模拟大模型（真实项目替换为 openai 调用）"""
    
    @staticmethod
    def chat(model: str, prompt: str) -> str:
        tokens = TokenCounter.estimate(prompt)
        return f"[{model}] 针对「{prompt[:30].replace(chr(10), ' ')}...」的回答（输入约{tokens}token）。"


class OptimizedService:
    """成本优化服务"""
    
    def __init__(self):
        self.cache = SemanticCache()
        self.budget = BudgetGuard()
        self.calls = 0
        self.total_cost = 0.0
        self.saved_by_cache = 0.0
        self.saved_by_routing = 0.0
        self.saved_by_compression = 0.0
        self.baseline_cost = 0.0   # 若全部用gpt-4且不压缩的成本
    
    def chat(self, prompt: str, force_model: str = None) -> Dict:
        # 基线成本（全gpt-4、不压缩）
        base_in = TokenCounter.estimate(prompt)
        base_out = 100
        self.baseline_cost += TokenCounter.cost("gpt-4", base_in, base_out)
        
        # 1. 缓存命中
        cached = self.cache.get(prompt)
        if cached is not None:
            self.saved_by_cache += TokenCounter.cost("gpt-4", base_in, base_out)
            return {"answer": cached, "cached": True, "cost": 0.0,
                    "model": "(cache)"}
        
        # 2. 提示词压缩
        compressed = PromptCompressor.compress(prompt)
        comp_in = TokenCounter.estimate(compressed)
        if comp_in < base_in:
            self.saved_by_compression += TokenCounter.cost(
                "gpt-4", base_in - comp_in, 0)
        
        # 3. 模型路由
        model = ModelRouter.route(compressed, force_model)
        if model != "gpt-4":
            self.saved_by_routing += TokenCounter.cost(
                "gpt-4", comp_in, base_out) - TokenCounter.cost(model, comp_in, base_out)
        
        # 4. 预算检查
        estimated = TokenCounter.cost(model, comp_in, base_out)
        if not self.budget.check(estimated):
            return {"answer": "当前请求量较大，请稍后重试。", "blocked": True,
                    "cost": 0.0, "model": model}
        
        # 5. 调用
        answer = MockLLM.chat(model, compressed)
        self.calls += 1
        
        # 6. 记账
        out_tokens = TokenCounter.estimate(answer)
        cost = TokenCounter.cost(model, comp_in, out_tokens)
        self.total_cost = round(self.total_cost + cost, 6)
        self.budget.record(cost)
        self.cache.set(prompt, answer)
        
        return {"answer": answer, "cached": False, "cost": cost,
                "model": model, "input_tokens": comp_in}
    
    def batch_chat(self, prompts, size: int = BATCH_SIZE) -> list:
        """批量合并调用"""
        results = []
        for batch in BatchProcessor.merge(prompts, size):
            results.append(self.chat(batch))
        return results
    
    def report(self) -> Dict:
        saved = self.saved_by_cache + self.saved_by_routing + self.saved_by_compression
        rate = (saved / self.baseline_cost * 100) if self.baseline_cost else 0
        return {
            "calls": self.calls,
            "total_cost": round(self.total_cost, 4),
            "baseline_cost": round(self.baseline_cost, 4),
            "saved_by_cache": round(self.saved_by_cache, 4),
            "saved_by_routing": round(self.saved_by_routing, 4),
            "saved_by_compression": round(self.saved_by_compression, 4),
            "total_saved": round(saved, 4),
            "savings_rate": f"{rate:.1f}%",
            "cache": self.cache.stats(),
            "budget": self.budget.stats(),
        }


service = OptimizedService()
