#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第38篇配套 · test_risk_kit.py
验证：六大风险/评估/协议/变更单/纠纷流程/文件生成

运行: python test_risk_kit.py
"""

import os
import shutil

from risk_kit import (
    RISKS, RiskAssessor, build_agreement, build_change_form,
    DISPUTE_FLOW, build_all, OUTPUT_DIR,
)


def main():
    print("=" * 66)
    print("🧪 项目风险预判与协议模板测试")
    print("=" * 66)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # 1. 六风险
    print("\n[1] 风险清单：")
    assert len(RISKS) == 6
    for name, info in RISKS.items():
        print(f"   {info['severity']}｜{name}")

    # 2. 评估
    print("\n[2] 风险评估：")
    r = RiskAssessor.assess(["需求无限新增", "尾款拖欠", "售后边界模糊"])
    print(f"   选中3项高风险 → {r['level']}（{r['score']}分），需签协议：{r['need_contract']}")
    assert r["level"] == "高风险" and r["need_contract"]
    print(f"   应对建议：{r['suggestions'][0][:40]}...")

    # 3. 协议
    print("\n[3] 协议模板：")
    agreement = build_agreement("XX科技", "张三", "L2 商用标准版", 1200, workdays=3)
    for section in ["项目需求与交付范围", "项目费用与付款节点", "素材、环境与API费用约定",
                    "验收标准", "售后约定", "知识产权与保密", "其他约定"]:
        assert section in agreement, f"缺少章节：{section}"
        print(f"   ✅ {section}")
    assert "600" in agreement  # 预付款50%
    assert "不含" in agreement
    assert "不承诺绝对零幻觉" in agreement or "不承诺绝对" in agreement

    # 4. 变更单
    print("\n[4] 需求变更确认单：")
    form = build_change_form()
    assert "变更内容" in form and "影响评估" in form and "确认" in form
    print("   ✅ 变更确认单完整")

    # 5. 纠纷流程
    print(f"\n[5] 纠纷处理流程：{len(DISPUTE_FLOW)} 步")
    assert len(DISPUTE_FLOW) == 5

    # 6. 生成文件
    print("\n[6] 生成交付文件：")
    paths = build_all()
    for p in paths:
        assert os.path.exists(p) and os.path.getsize(p) > 200
        print(f"   ✅ {os.path.basename(p)}（{os.path.getsize(p)}字节）")
    assert len(paths) == 3

    print("\n✅ 风险预判与协议工具包测试通过")


if __name__ == "__main__":
    main()
