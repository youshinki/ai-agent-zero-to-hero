#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第34篇配套 · test_xianyu_ops.py
验证发布包：账号配置/3套标题/4段详情/定价/运营计划/发布文案

运行: python test_xianyu_ops.py
"""

import os
import shutil

from xianyu_ops import (
    AccountSetup, TITLE_TEMPLATES, DetailPage, PRICING,
    REPLY_RULES, OPERATION_PLAN, build_listing_package, OUTPUT_DIR,
)


def main():
    print("=" * 66)
    print("🧪 闲鱼零成本获客工具包测试")
    print("=" * 66)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # 1. 账号配置
    print("\n[1] 账号配置：")
    acc = AccountSetup.generate()
    assert "昵称" in acc and "简介" in acc and "权重维护" in acc
    print(f"   昵称：{AccountSetup.NICKNAME}")
    print("   ✅ 账号配置完整")

    # 2. 标题模板
    print("\n[2] 标题模板：")
    assert len(TITLE_TEMPLATES) == 3
    for scene, title in TITLE_TEMPLATES.items():
        print(f"   ✅ {scene}：{title[:28]}...")
        assert "AI" in title and "知识库" in title

    # 3. 详情页
    print("\n[3] 详情页：")
    assert len(DetailPage.SECTIONS) == 4
    for title in DetailPage.SECTIONS:
        print(f"   ✅ {title}")

    # 4. 定价
    print("\n[4] 定价区间：")
    for name, info in PRICING.items():
        print(f"   {name}：{info['price']}元")
    assert PRICING["基础版"]["price"] == 800
    assert PRICING["标准版"]["price"] == 1200

    # 5. 咨询规则与运营
    print("\n[5] 咨询规则与运营计划：")
    print(f"   咨询规则 {len(REPLY_RULES)} 条")
    print(f"   运营计划 {len(OPERATION_PLAN)} 个维度")
    assert len(REPLY_RULES) >= 4

    # 6. 生成发布包
    print("\n[6] 生成发布包：")
    paths = build_listing_package("标准版")
    for p in paths:
        assert os.path.exists(p) and os.path.getsize(p) > 100
        print(f"   ✅ {os.path.basename(p)}（{os.path.getsize(p)}字节）")
    assert len(paths) == 6

    # 7. 发布文案可直接使用
    listing_path = os.path.join(OUTPUT_DIR, "06_发布文案.md")
    with open(listing_path, encoding="utf-8") as f:
        listing = f.read()
    assert "标题" in listing and "详情" in listing and "1200" in listing
    print("\n[7] 发布文案校验：✅ 可直接复制使用")

    print("\n✅ 闲鱼获客工具包测试通过")


if __name__ == "__main__":
    main()
