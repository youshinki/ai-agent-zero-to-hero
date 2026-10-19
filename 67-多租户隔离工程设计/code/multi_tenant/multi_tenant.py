#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第67篇配套完整项目代码 · multi_tenant.py
多租户隔离：知识库隔离、资源配额、数据权限与计费隔离

  1. 租户上下文
  2. 知识库硬隔离（tenant_id 过滤）
  3. 资源配额（QPS/Token/存储）
  4. 计费隔离（按租户统计）
  5. 跨租户访问检测
==========================================================================
"""

import time
from typing import Dict, List, Optional


# ======================================================================
# 一、租户上下文
# ======================================================================

class TenantContext:
    def __init__(self, tenant_id: str, user_id: str = "",
                 role: str = "user"):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.role = role


# ======================================================================
# 二、知识库隔离
# ======================================================================

class Document:
    def __init__(self, doc_id: str, tenant_id: str, content: str):
        self.doc_id = doc_id
        self.tenant_id = tenant_id
        self.content = content


class IsolatedKnowledgeBase:
    def __init__(self):
        self.docs: List[Document] = []
        self.cross_tenant_attempts = 0
    
    def add(self, tenant_id: str, doc_id: str, content: str):
        self.docs.append(Document(doc_id, tenant_id, content))
    
    def search(self, ctx: TenantContext, query: str) -> List[Dict]:
        # 硬隔离：只返回本租户文档
        results = []
        for d in self.docs:
            if d.tenant_id != ctx.tenant_id:
                continue
            score = len(set(query) & set(d.content)) / max(len(set(query)), 1)
            if score > 0.1:
                results.append({"doc_id": d.doc_id, "content": d.content,
                                "score": round(score, 3)})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:3]
    
    def get_document(self, ctx: TenantContext, doc_id: str) -> Optional[Document]:
        for d in self.docs:
            if d.doc_id == doc_id:
                if d.tenant_id != ctx.tenant_id:
                    self.cross_tenant_attempts += 1
                    raise PermissionError("跨租户访问被拒绝")
                return d
        return None


# ======================================================================
# 三、配额
# ======================================================================

class QuotaManager:
    def __init__(self):
        self.quotas: Dict[str, Dict] = {}
        self.usage: Dict[str, Dict] = {}
    
    def set_quota(self, tenant_id: str, requests_per_min: int = 60,
                  tokens_per_month: int = 100000, storage_mb: int = 100):
        self.quotas[tenant_id] = {
            "requests_per_min": requests_per_min,
            "tokens_per_month": tokens_per_month,
            "storage_mb": storage_mb,
        }
        self.usage.setdefault(tenant_id, {
            "requests": 0, "window_start": time.time(),
            "tokens": 0, "storage_mb": 0,
        })
    
    def check_request(self, tenant_id: str) -> Dict:
        q = self.quotas.get(tenant_id)
        if not q:
            return {"allowed": False, "reason": "未配置租户"}
        u = self.usage[tenant_id]
        now = time.time()
        if now - u["window_start"] >= 60:
            u["requests"] = 0
            u["window_start"] = now
        if u["requests"] >= q["requests_per_min"]:
            return {"allowed": False, "reason": "QPS超限"}
        if u["tokens"] >= q["tokens_per_month"]:
            return {"allowed": False, "reason": "Token配额用尽"}
        u["requests"] += 1
        return {"allowed": True}
    
    def consume_tokens(self, tenant_id: str, tokens: int) -> Dict:
        u = self.usage[tenant_id]
        q = self.quotas[tenant_id]
        if u["tokens"] + tokens > q["tokens_per_month"]:
            return {"ok": False, "reason": "Token配额不足"}
        u["tokens"] += tokens
        return {"ok": True, "remaining": q["tokens_per_month"] - u["tokens"]}
    
    def storage_status(self, tenant_id: str) -> Dict:
        q, u = self.quotas[tenant_id], self.usage[tenant_id]
        return {"used": u["storage_mb"], "limit": q["storage_mb"],
                "ratio": f"{u['storage_mb'] / q['storage_mb'] * 100:.0f}%"}


# ======================================================================
# 四、计费隔离
# ======================================================================

class Billing:
    PRICE_PER_1K = 0.002
    
    def __init__(self):
        self.records: Dict[str, Dict] = {}
    
    def record(self, tenant_id: str, tokens: int):
        r = self.records.setdefault(tenant_id, {"tokens": 0, "cost": 0.0,
                                                "calls": 0})
        r["tokens"] += tokens
        r["calls"] += 1
        r["cost"] = round(r["tokens"] / 1000 * self.PRICE_PER_1K, 6)
        return r
    
    def get(self, tenant_id: str) -> Dict:
        return self.records.get(tenant_id, {"tokens": 0, "cost": 0.0, "calls": 0})
    
    def all(self) -> Dict:
        return self.records


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("🏢 多租户隔离演示")
    print("=" * 66)
    
    kb = IsolatedKnowledgeBase()
    kb.add("tenant_a", "a1", "A公司产品手册：支持RAG知识库")
    kb.add("tenant_a", "a2", "A公司定价：标准版19800元")
    kb.add("tenant_b", "b1", "B公司内部制度：考勤9点")
    
    ctx_a = TenantContext("tenant_a", "alice")
    ctx_b = TenantContext("tenant_b", "bob")
    
    print("\n[1] 知识库硬隔离：")
    r = kb.search(ctx_a, "产品手册")
    print(f"   tenant_a 检索：{[x['doc_id'] for x in r]}")
    r = kb.search(ctx_b, "产品手册")
    print(f"   tenant_b 检索：{[x['doc_id'] for x in r]}")
    assert all(x["doc_id"].startswith("a") for x in kb.search(ctx_a, "定价"))
    
    print("\n[2] 跨租户访问拦截：")
    try:
        kb.get_document(ctx_a, "b1")
    except PermissionError as e:
        print(f"   🛡️ {e}")
    print(f"   跨租户尝试次数：{kb.cross_tenant_attempts}")
    
    print("\n[3] 配额：")
    qm = QuotaManager()
    qm.set_quota("tenant_a", requests_per_min=3, tokens_per_month=100)
    for i in range(3):
        print(f"   第{i+1}次：{qm.check_request('tenant_a')}")
    print(f"   第4次：{qm.check_request('tenant_a')}")
    print(f"   Token消耗：{qm.consume_tokens('tenant_a', 60)}")
    
    print("\n[4] 计费隔离：")
    bill = Billing()
    bill.record("tenant_a", 1200)
    bill.record("tenant_b", 500)
    bill.record("tenant_a", 800)
    for t, info in bill.all().items():
        print(f"   {t}：{info['calls']}次调用，{info['tokens']}token，¥{info['cost']}")


if __name__ == "__main__":
    demo()
