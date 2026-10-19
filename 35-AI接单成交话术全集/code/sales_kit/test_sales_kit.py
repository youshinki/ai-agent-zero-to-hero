#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第35篇配套 · test_sales_kit.py
验证：六阶段话术、四大异议、红线、模拟陪练、手册生成

运行: python test_sales_kit.py
"""

import os
import shutil

from sales_kit import (
    SCRIPTS, OBJECTIONS, RED_LINES, SalesSimulator,
    generate_manual, OUTPUT_DIR,
)


def main():
    print("=" * 66)
    print("🧪 AI接单成交话术工具包测试")
    print("=" * 66)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # 1. 六阶段
    print("\n[1] 六阶段话术：")
    assert len(SCRIPTS) == 6
    for stage in SCRIPTS:
        print(f"   ✅ {stage}")

    # 2. 四大异议
    print("\n[2] 高频异议：")
    assert len(OBJECTIONS) == 4
    for name in OBJECTIONS:
        print(f"   ✅ {name}")
    assert "Demo" in OBJECTIONS["比价"]["reply"] or "商用" in OBJECTIONS["比价"]["reply"]

    # 3. 红线
    print(f"\n[3] 沟通红线：{len(RED_LINES)} 条")
    assert len(RED_LINES) == 4

    # 4. 模拟陪练
    print("\n[4] 模拟陪练：")
    sim = SalesSimulator()
    test_inputs = [
        "别人才300块，你怎么这么贵",
        "能不能先试用，满意再付款",
        "资料会不会泄露啊",
        "我想再加几个功能",
        "你们报价多少",
        "你好，在吗",
    ]
    for q in test_inputs:
        r = sim.match(q)
        tag = "、".join(r.get("points", [])[:2])
        print(f"   客户：{q[:16]}... → 要点：{tag}")
    # 校验匹配正确
    assert "低价" in sim.match("别人才300块")["reply"] or "商用" in sim.match("别人才300块")["reply"]
    assert "私有化" in sim.match("资料会不会泄露")["reply"]

    # 5. 手册生成
    print("\n[5] 话术手册生成：")
    manual = generate_manual()
    path = os.path.join(OUTPUT_DIR, "话术手册.md")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(manual)
    assert os.path.exists(path)
    for key in ["六阶段标准话术", "高频异议应对", "沟通红线"]:
        assert key in manual
    print(f"   ✅ {path}（{len(manual)}字）")

    print("\n✅ 成交话术工具包测试通过")


if __name__ == "__main__":
    main()
