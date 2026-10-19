#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第67篇配套 · test_multi_tenant.py
"""

from multi_tenant import (
    TenantContext, IsolatedKnowledgeBase, QuotaManager, Billing, demo,
)


def main():
    print("=" * 66)
    print("🧪 多租户隔离测试")
    print("=" * 66)

    print("\n[1] 知识库隔离：")
    kb = IsolatedKnowledgeBase()
    kb.add("tenant_a", "a1", "A公司产品手册：RAG知识库")
    kb.add("tenant_a", "a2", "A公司定价19800元")
    kb.add("tenant_b", "b1", "B公司制度：考勤9点")
    ca = TenantContext("tenant_a", "alice")
    cb = TenantContext("tenant_b", "bob")
    ra = kb.search(ca, "定价")
    rb = kb.search(cb, "定价")
    assert [x["doc_id"] for x in ra] == ["a2"]
    assert rb == []
    print(f"   A检索：{[x['doc_id'] for x in ra]}｜B检索：{rb}")

    print("\n[2] 跨租户拦截：")
    try:
        kb.get_document(ca, "b1")
        assert False
    except PermissionError:
        pass
    assert kb.cross_tenant_attempts == 1
    print("   ✅ 跨租户访问被拒绝")

    print("\n[3] 配额：")
    qm = QuotaManager()
    qm.set_quota("t1", requests_per_min=2, tokens_per_month=100)
    assert qm.check_request("t1")["allowed"]
    assert qm.check_request("t1")["allowed"]
    r = qm.check_request("t1")
    assert not r["allowed"] and "QPS" in r["reason"]
    print(f"   ✅ QPS超限：{r['reason']}")
    # 时间窗重置
    qm.usage["t1"]["window_start"] -= 61
    assert qm.check_request("t1")["allowed"]
    print("   ✅ 时间窗重置后恢复")
    # token
    r = qm.consume_tokens("t1", 100)
    assert r["ok"]
    r = qm.consume_tokens("t1", 1)
    assert not r["ok"]
    print(f"   ✅ Token配额耗尽：{r['reason']}")

    print("\n[4] 计费隔离：")
    b = Billing()
    b.record("t1", 1000)
    b.record("t1", 500)
    b.record("t2", 2000)
    assert b.get("t1")["tokens"] == 1500 and b.get("t2")["tokens"] == 2000
    assert len(b.all()) == 2
    print(f"   ✅ t1/t2 独立计费：{b.all()}")

    print("\n[5] 演示：")
    demo()
    print("\n✅ 多租户隔离测试通过")


if __name__ == "__main__":
    main()
