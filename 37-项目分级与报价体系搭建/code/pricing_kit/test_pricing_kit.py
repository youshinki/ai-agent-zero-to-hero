#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第37篇配套 · test_pricing_kit.py
验证：四级分级/5维评估/报价核算/增值项/变更规则/手册生成

运行: python test_pricing_kit.py
"""

import os
import shutil

from pricing_kit import (
    TIERS, ADDONS, ProjectEvaluator, QuoteCalculator,
    CHANGE_RULES, QUOTE_SCRIPTS, build_manual, OUTPUT_DIR,
)


def main():
    print("=" * 66)
    print("🧪 项目分级与报价体系测试")
    print("=" * 66)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # 1. 四级分级
    print("\n[1] 四级项目分级：")
    assert len(TIERS) == 4
    for name, info in TIERS.items():
        print(f"   {name}：¥{info['price']}（{info['hours']}）")
    assert TIERS["L2 商用标准版"]["price"] == 1200

    # 2. 五维评估
    print("\n[2] 五维评估定级：")
    cases = [
        {"文档规模与类型": "low", "定制开发需求": "low", "第三方对接需求": "low",
         "部署环境要求": "low", "售后与运维要求": "low"},
        {"文档规模与类型": "mid", "定制开发需求": "low", "第三方对接需求": "low",
         "部署环境要求": "mid", "售后与运维要求": "low"},
        {"文档规模与类型": "mid", "定制开发需求": "high", "第三方对接需求": "mid",
         "部署环境要求": "mid", "售后与运维要求": "mid"},
        {"文档规模与类型": "high", "定制开发需求": "high", "第三方对接需求": "high",
         "部署环境要求": "high", "售后与运维要求": "high"},
    ]
    for c in cases:
        r = ProjectEvaluator.evaluate(c)
        print(f"   总分{r['total_score']} → {r['tier']}")
    assert ProjectEvaluator.evaluate(cases[0])["tier"].startswith("L1")
    assert ProjectEvaluator.evaluate(cases[3])["tier"].startswith("L4")

    # 3. 报价核算
    print("\n[3] 报价核算：")
    calc = QuoteCalculator(day_rate=800)
    q = calc.quote("L2 商用标准版", workdays=2, reuse_ratio=0.5,
                   addons=["服务器部署、环境搭建"])
    for k in ["base_cost", "after_reuse", "risk_cost", "addon_cost",
              "calculated_total", "tier_reference_price", "suggested_price"]:
        print(f"   {k}: {q[k]}")
    assert q["suggested_price"] >= TIERS["L2 商用标准版"]["price"]

    # 4. 增值项
    print(f"\n[4] 增值项：{len(ADDONS)} 项")
    assert "月度运维托管服务" in ADDONS

    # 5. 变更规则与话术
    print(f"\n[5] 变更规则：{len(CHANGE_RULES)} 条")
    print(f"   报价话术：{len(QUOTE_SCRIPTS)} 组")
    assert len(CHANGE_RULES) == 4 and len(QUOTE_SCRIPTS) == 3

    # 6. 手册
    print("\n[6] 手册生成：")
    manual = build_manual()
    path = os.path.join(OUTPUT_DIR, "报价手册.md")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(manual)
    for key in ["四级项目分级", "5维评估定级", "增值项", "需求变更规则", "报价话术"]:
        assert key in manual
    print(f"   ✅ {path}（{len(manual)}字）")

    print("\n✅ 报价体系测试通过")


if __name__ == "__main__":
    main()
