#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第45篇配套 · test_cost_control.py
验证：计量/缓存/压缩/路由/降级/预算/告警/降本报告

运行: python test_cost_control.py
"""

from cost_engine import (
    Meter, SemanticCache, Compressor, Router,
    BudgetGuard, CostOptimizer, demo,
)


def main():
    print("=" * 66)
    print("🧪 极致成本控制测试")
    print("=" * 66)

    # 1. 计量
    print("\n[1] Token 计量与成本：")
    t = Meter.tokens("请分析这份企业知识库部署方案")
    print(f"   文本 → {t} token")
    for m in ["gpt-4", "deepseek-chat", "qwen-turbo"]:
        print(f"   {m}: ¥{Meter.cost(m, t, 100)}")
    assert Meter.cost("gpt-4", 1000, 0) > Meter.cost("qwen-turbo", 1000, 0)

    # 2. 缓存
    print("\n[2] 语义缓存：")
    c = SemanticCache(ttl=60)
    assert c.get("你好") is None
    c.set("你好", "你好！")
    assert c.get("你好") == "你好！"
    assert c.get("你 好") == "你好！"  # 归一化命���
    print(f"   {c.stats()}")
    assert c.hits == 2

    # 3. 压缩
    print("\n[3] 提示词压缩：")
    verbose = "请注意，你是一个非常非常重要的助手，请务必尽量完整地回答。" * 4
    comp = Compressor.compress(verbose)
    print(f"   {len(verbose)}字 → {len(comp)}字")
    assert len(comp) < len(verbose)

    # 4. 路由与降级
    print("\n[4] 模型路由：")
    cases = ["你好", "翻译这段文字", "请深度分析这份复杂报告并给出完整方案与风险评估"]
    for q in cases:
        print(f"   「{q[:16]}...」→ {Router.route(q)}")
    assert Router.route("你好") == "qwen-turbo"
    print(f"   gpt-4 降级链：gpt-4 → {Router.fallback('gpt-4')} → {Router.fallback(Router.fallback('gpt-4'))}")

    # 5. 预算告警
    print("\n[5] 预算与告警：")
    b = BudgetGuard(daily=1.0, alert_ratio=0.8)
    b.record(0.85)
    allowed = b.check(0.01)
    print(f"   已用0.85/1.0，新请求放行：{allowed}，告警数：{len(b.alerts)}")
    assert allowed and len(b.alerts) == 1
    blocked = b.check(0.5)
    print(f"   再请求0.5 → 放行：{blocked}")
    assert blocked is False

    # 6. 完整降本演示
    print("\n[6] 完整降本演示：")
    r = demo()
    assert float(r["savings_rate"].rstrip("%")) >= 50

    print("\n✅ 极致成本控制测试通过")


if __name__ == "__main__":
    main()
