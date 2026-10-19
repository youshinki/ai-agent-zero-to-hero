#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第32篇配套 · test_delivery_kit.py
验证交付工具包：生成4份标准文档并检查关键内容

运行: python test_delivery_kit.py
"""

import os
import shutil

from delivery_kit import (
    DeliveryChecklist, UserManual, AfterSalePolicy,
    RequirementForm, generate_all, OUTPUT_DIR,
)


def main():
    print("=" * 66)
    print("🧪 标准化交付文档测试")
    print("=" * 66)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # 1. 交付清单
    checklist = DeliveryChecklist.generate("企业私有知识库", "XX科技有限公司")
    print(f"\n[1] 交付清单：{len(checklist)}字")
    for key in ["交付成品内容", "交付配套文档", "标准验收项", "双方确认"]:
        assert key in checklist, f"缺失章节：{key}"
        print(f"   ✅ {key}")

    # 2. 使用手册
    manual = UserManual.generate()
    print(f"\n[2] 使用手册：{len(manual)}字")
    for key in ["系统介绍", "基础使用方式", "资料更新方式", "常见问题"]:
        assert key in manual
        print(f"   ✅ {key}")

    # 3. 售后边界
    policy = AfterSalePolicy.generate()
    print(f"\n[3] 售后方案：{len(policy)}字")
    assert "免费售后范围" in policy and "有偿服务范围" in policy
    assert len(AfterSalePolicy.FREE_ITEMS) >= 4
    assert len(AfterSalePolicy.PAID_ITEMS) >= 4
    print(f"   免费项：{len(AfterSalePolicy.FREE_ITEMS)} 条")
    print(f"   有偿项：{len(AfterSalePolicy.PAID_ITEMS)} 条")

    # 4. 需求确认书
    form = RequirementForm.generate()
    print(f"\n[4] 需求确认书：{len(form)}字")
    assert "不在本次范围内" in form, "必须声明范围边界"
    print("   ✅ 已声明范围边界")

    # 5. 批量生成
    print("\n[5] 批量生成文档到 output/：")
    paths = generate_all("企业私有知识库", "XX科技有限公司")
    for p in paths:
        assert os.path.exists(p) and os.path.getsize(p) > 100
        print(f"   ✅ {p}（{os.path.getsize(p)}字节）")
    assert len(paths) == 4

    print("\n✅ 标准化交付文档测试通过")


if __name__ == "__main__":
    main()
