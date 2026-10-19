#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第36篇配套 · test_channel_matrix.py
验证：三渠道策略 / 30天排期 / 漏斗 / ROI / 私域SOP / 方案生成

运行: python test_channel_matrix.py
"""

import os
import shutil

from channel_matrix import (
    CHANNELS, build_calendar, Funnel, roi_table,
    PRIVATE_SOP, build_plan, OUTPUT_DIR,
)


def main():
    print("=" * 66)
    print("🧪 多渠道矩阵获客测试")
    print("=" * 66)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # 1. 三渠道
    print("\n[1] 三渠道策略：")
    assert len(CHANNELS) == 3
    for name in CHANNELS:
        print(f"   ✅ {name}：{CHANNELS[name]['frequency']}")

    # 2. 30天排期
    print("\n[2] 30天排期：")
    cal = build_calendar(30)
    assert len(cal) == 30
    total_tasks = sum(len(x["tasks"]) for x in cal)
    print(f"   共 {len(cal)} 天，{total_tasks} 条内容任务")
    days_with_bili = sum(1 for x in cal if any(t[0] == "B站" for t in x["tasks"]))
    days_with_xhs = sum(1 for x in cal if any(t[0] == "小红书" for t in x["tasks"]))
    print(f"   B站：{days_with_bili} 天 | 小红书：{days_with_xhs} 天")
    assert days_with_xhs >= 10

    # 3. 漏斗
    print("\n[3] 获客漏斗：")
    f = Funnel()
    for c in f.conversions():
        print(f"   {c['from']}({c['from_count']}) → {c['to']}({c['to_count']})：{c['rate']}")
    assert len(f.conversions()) == 4
    opt = f.optimize("成交", 8)
    print(f"   优化成交 5→8：提升 {opt['growth']}")

    # 4. ROI
    print("\n[4] 渠道 ROI：")
    rows = roi_table()
    for r in rows:
        print(f"   {r['channel']}：投入¥{r['cost']} 获客{r['leads']} 预计收入¥{r['revenue']} ROI {r['roi']}")
    assert len(rows) == 5

    # 5. 私域 SOP
    print(f"\n[5] 私域 SOP：{len(PRIVATE_SOP)} 天内容")

    # 6. 方案生成
    print("\n[6] 方案生成：")
    plan = build_plan(30)
    path = os.path.join(OUTPUT_DIR, "矩阵获客方案.md")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(plan)
    for key in ["三渠道策略", "内容排期", "获客漏斗", "渠道 ROI", "私域朋友圈 SOP"]:
        assert key in plan, f"缺少 {key}"
    print(f"   ✅ {path}（{len(plan)}字）")

    print("\n✅ 多渠道矩阵获客测试通过")


if __name__ == "__main__":
    main()
