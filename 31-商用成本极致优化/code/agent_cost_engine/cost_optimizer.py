#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第31篇配套完整项目代码 · cost_optimizer.py
商用成本优化引擎：
  1. TokenCounter     —— 精确计量
  2. PromptCompressor —— 提示词压缩
  3. SemanticCache    —— 结果缓存
  4. ModelRouter      —— 模型降级路由
  5. BatchProcessor   —— 批量合并
  6. BudgetGuard      —— 预算熔断
==========================================================================
"""

import hashlib
import re
import time
from typing import Dict, List, Optional

from config import (
    MODEL_PRICES, CACHE_TTL_SECONDS, DAILY_BUDGET_YUAN, MONTHLY_BUDGET_YUAN,
    MAX_INPUT_TOKENS, BATCH_SIZE, ENABLE_CACHE, ENABLE_ROUTING,
)


# ======================================================================
# 1. Token 计量
# ======================================================================

class TokenCounter:
    @staticmethod
    def estimate(text: str) -> int:
        """中文≈1.5倍字符，英文≈0.3倍"""
        if not text:
            return 0
        chinese = len(re.findall(r"[\u4e00-\u9fa5]", text))
        other = len(text) - chinese
        return int(chinese * 1.5 + other * 0.3) + 1
    
    @staticmethod
    def cost(model: str, input_tokens: int, output_tokens: int) -> float:
        price = MODEL_PRICES.get(model, MODEL_PRICES["gpt-3.5-turbo"])
        return round(
            input_tokens / 1000 * price["input"] +
            output_tokens / 1000 * price["output"], 6
        )


# ======================================================================
# 2. 提示词压缩
# ======================================================================

class PromptCompressor:
    """提示词瘦身：去冗余、去重复、截断长上下文"""
    
    FILLER_PATTERNS = [
        r"请注意", r"请记住", r"你是一个", r"你是一位", r"你需要",
        r"非常重要", r"一定要", r"务必", r"尽可能地", r"尽量",
        r"非常非常", r"十分", r"特别特别",
    ]
    
    @classmethod
    def compress(cls, prompt: str, max_tokens: int = MAX_INPUT_TOKENS) -> str:
        text = prompt
        # 1. 去口头禅/冗余修饰
        for pat in cls.FILLER_PATTERNS:
            text = re.sub(pat, "", text)
        # 2. 合并多余空白
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        # 3. 超长截断（保留首尾，丢弃中间低价值部分）
        if TokenCounter.estimate(text) > max_tokens:
            max_chars = int(max_tokens / 1.5)
            head = int(max_chars * 0.7)
            tail = max_chars - head
            text = text[:head] + "\n...(省略部分内容)...\n" + text[-tail:]
        return text.strip()


# ======================================================================
# 3. 语义缓存
# ======================================================================

class SemanticCache:
    """结果缓存：相同/近似请求直接命中，零API成本"""
    
    def __init__(self, ttl: int = CACHE_TTL_SECONDS):
        self.ttl = ttl
        self._store: Dict[str, Dict] = {}
        self.hits = 0
        self.misses = 0
    
    @staticmethod
    def _normalize(text: str) -> str:
        """归一化：去空格、标点、大小写"""
        t = re.sub(r"[\s，。！？、,.!?]", "", text.lower())
        return t
    
    def _key(self, prompt: str) -> str:
        return hashlib.md5(self._normalize(prompt).encode()).hexdigest()
    
    def get(self, prompt: str) -> Optional[str]:
        if not ENABLE_CACHE:
            return None
        key = self._key(prompt)
        item = self._store.get(key)
        if not item:
            self.misses += 1
            return None
        if time.time() - item["time"] > self.ttl:
            del self._store[key]
            self.misses += 1
            return None
        self.hits += 1
        item["used"] += 1
        return item["answer"]
    
    def set(self, prompt: str, answer: str):
        self._store[self._key(prompt)] = {
            "answer": answer, "time": time.time(), "used": 0,
        }
    
    def stats(self) -> Dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits, "misses": self.misses,
            "hit_rate": f"{self.hits / total * 100:.1f}%" if total else "0%",
            "size": len(self._store),
        }


# ======================================================================
# 4. 模型路由 / 降级
# ======================================================================

class ModelRouter:
    """按任务复杂度选择模型：简单任务用便宜模型"""
    
    @staticmethod
    def route(prompt: str, force_model: Optional[str] = None) -> str:
        if force_model:
            return force_model
        if not ENABLE_ROUTING:
            return "gpt-4"
        
        text = prompt.lower()
        tokens = TokenCounter.estimate(prompt)
        
        # 简单任务 → 最便宜模型
        simple_keys = ["你好", "天气", "时间", "翻译", "计算", "是什么", "多少"]
        if tokens < 200 and any(k in text for k in simple_keys):
            return "qwen-turbo"
        # 中等任务 → 中端模型
        if tokens < 800:
            return "deepseek-chat"
        # 复杂任务 → 高端模型
        return "gpt-4"


# ======================================================================
# 5. 批量合并
# ======================================================================

class BatchProcessor:
    """把多个小请求合并为一次调用，减少请求开销"""
    
    @staticmethod
    def merge(items: List[str], size: int = BATCH_SIZE) -> List[str]:
        batches = []
        for i in range(0, len(items), size):
            group = items[i:i + size]
            merged = "\n---\n".join(
                f"任务{j+1}：{x}" for j, x in enumerate(group)
            )
            batches.append(merged)
        return batches


# ======================================================================
# 6. 预算熔断
# ======================================================================

class BudgetGuard:
    def __init__(self, daily: float = DAILY_BUDGET_YUAN,
                 monthly: float = MONTHLY_BUDGET_YUAN):
        self.daily = daily
        self.monthly = monthly
        self.daily_used = 0.0
        self.monthly_used = 0.0
        self.blocked = 0
    
    def check(self, estimated_cost: float) -> bool:
        if self.daily_used + estimated_cost > self.daily:
            self.blocked += 1
            return False
        if self.monthly_used + estimated_cost > self.monthly:
            self.blocked += 1
            return False
        return True
    
    def record(self, cost: float):
        self.daily_used = round(self.daily_used + cost, 6)
        self.monthly_used = round(self.monthly_used + cost, 6)
    
    def stats(self) -> Dict:
        return {
            "daily_used": round(self.daily_used, 4),
            "daily_budget": self.daily,
            "monthly_used": round(self.monthly_used, 4),
            "monthly_budget": self.monthly,
            "blocked_requests": self.blocked,
        }
