#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第40篇配套 · test_review_kit.py
验证：经营指标/等级分布/渠道ROI/CLV/漏斗/复盘报告

运行: python test_review_kit.py
"""

import os
import shutil

from review_kit import (
    calculate_clv,
    funnel_analysis,
    build_report,
    build_demo_ledger,
    OUTPUT_DIR,
)


def main():
    print("=" * 66)
    print("🧪 商业化全链路复盘测试")
    print("=" * 66)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    ledger = build_demo_ledger()

    # 1. 经营指标
    print("\n[1] 经营指标：")
    m = ledger.metrics()
    for k, v in m.items():
        print(f"   {k}: {v}")
    assert m["projects"] == 5
    assert m["profit"] == m["revenue"] - m["cost"]

    # 2. 等级分布
    print("\n[2] 项目等级分布：")
    dist = ledger.tier_distribution()
    for tier, info in dist.items():
        print(f"   {tier}: {info['count']}个 / ¥{info['revenue']}")
    assert sum(x["count"] for x in dist.values()) == 5

    # 3. 渠道 ROI
    print("\n[3] 渠道 ROI：")
    rows = ledger.channel_roi()
    for r in rows[:3]:
        print(f"   {r['channel']}: 投入¥{r['cost']} 获客{r['leads']} ROI {r['roi']}")
    assert rows[0]["revenue"] >= rows[-1]["revenue"]

    # 4. CLV
    print("\n[4] 客户终身价值：")
    clv = calculate_clv(1800, 500, 12)
    for k, v in clv.items():
        print(f"   {k}: {v}")
    assert clv["clv"] == 1800 + 500 * 12 + 1800 * 0.2

    # 5. 漏斗
    print("\n[5] 获客漏斗：")
    f = funnel_analysis()
    for c in f["conversions"]:
        print(f"   {c['from']}({c['from_count']}) → {c['to']}({c['to_count']}): {c['rate']}")

    # 6. 报告
    print("\n[6] 复盘报告：")
    report = build_report(ledger, clv)
    path = os.path.join(OUTPUT_DIR, "商业化复盘报告.md")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    for key in ["经营概况", "项目明细", "等级分布", "渠道 ROI", "客户终身价值", "关键结论"]:
        assert key in report, f"缺少 {key}"
    print(f"   ✅ {path}（{len(report)}字）")

    print("\n✅ 商业化复盘测试通过")


if __name__ == "__main__":
    main()
