#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第39篇配套 · test_delivery_ops.py
验证：检查清单/托管套餐/排期/收入LTV/交付报告

运行: python test_delivery_ops.py
"""

import os
import shutil

from delivery_ops import (
    CHECKLIST, PLANS, SCHEDULE, calculate_revenue,
    build_checklist, build_handover_report, generate_all, OUTPUT_DIR,
)


def main():
    print("=" * 66)
    print("🧪 交付上线与运维托管测试")
    print("=" * 66)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # 1. 检查清单
    print("\n[1] 上线检查清单：")
    assert len(CHECKLIST) == 4
    for cat, items in CHECKLIST.items():
        print(f"   ✅ {cat}：{len(items)} 项")
    cl = build_checklist("企业知识库")
    assert "- [ ]" in cl and "验收签字" in cl

    # 2. 托管套餐
    print("\n[2] 运维托管套餐：")
    assert len(PLANS) == 3
    for name, info in PLANS.items():
        print(f"   {name}：{info['price']}")

    # 3. 排期
    print(f"\n[3] 运维排期：{len(SCHEDULE)} 个维度")
    assert "每日" in SCHEDULE and "每周" in SCHEDULE and "每月" in SCHEDULE

    # 4. 收入与LTV
    print("\n[4] 托管收入与LTV：")
    rev = calculate_revenue(5, 3000)
    for k, v in rev.items():
        print(f"   {k}: {v}")
    assert rev["annual_revenue"] == 180000
    assert rev["ltv_3y_per_client"] == 108000

    # 5. 交付报告
    print("\n[5] 交付报告：")
    report = build_handover_report("企业知识库", "XX科技",
                                   ["文档入库", "语义检索", "溯源引用"])
    for key in ["交付功能清单", "上线检查结论", "售后与运维", "后续迭代建议"]:
        assert key in report
    print("   ✅ 报告包含4个章节")

    # 6. 生成全部
    print("\n[6] 生成全部文档：")
    paths = generate_all()
    for p in paths:
        assert os.path.exists(p) and os.path.getsize(p) > 100
        print(f"   ✅ {os.path.basename(p)}（{os.path.getsize(p)}字节）")
    assert len(paths) == 4

    print("\n✅ 交付运维工具包测试通过")


if __name__ == "__main__":
    main()
