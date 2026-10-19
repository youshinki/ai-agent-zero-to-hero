#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第33篇配套 · test_case_builder.py
验证：3套案例构建 + 包装素材 + 破零策略

运行: python test_case_builder.py
"""

import os
import shutil

from case_builder import CASES, build_all_cases, OUTPUT_DIR, CasePackaging


def main():
    print("=" * 66)
    print("🧪 零案例破局 · 案例构建测试")
    print("=" * 66)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # 1. 三套案例
    print(f"\n[1] 构建 {len(CASES)} 套案例：")
    results = build_all_cases()
    assert len(results) == 3
    for r in results:
        print(f"   ✅ {r['key']}：{r['docs']}份文档 / {r['questions']}个问答")
        assert os.path.exists(os.path.join(r["dir"], "README.md"))
        assert os.path.exists(os.path.join(r["dir"], "demo_qa.md"))
        assert os.path.isdir(os.path.join(r["dir"], "data"))

    # 2. 资料文件完整性
    print("\n[2] 资料文件校验：")
    for case_key, case in CASES.items():
        data_dir = os.path.join(OUTPUT_DIR, case_key, "data")
        files = os.listdir(data_dir)
        print(f"   {case['name']}：{len(files)} 个资料文件")
        assert len(files) == len(case["docs"])

    # 3. 演示问答
    print("\n[3] 演示问答预览（案例1）：")
    demo_path = os.path.join(OUTPUT_DIR, "case1_企业制度知识库", "demo_qa.md")
    with open(demo_path, encoding="utf-8") as f:
        demo = f.read()
    print(demo[:220].replace("\n", "\n   "))
    assert demo.count("**Q") == 3

    # 4. 包装素材
    print("\n[4] 包装素材：")
    for case_key, case in CASES.items():
        case_dir = os.path.join(OUTPUT_DIR, case_key)
        for name in ["视频脚本.md", "接单文案.md"]:
            path = os.path.join(case_dir, name)
            assert os.path.exists(path), f"缺少 {path}"
        print(f"   ✅ {case['name']}：视频脚本 + 接单文案")

    strategy = os.path.join(OUTPUT_DIR, "首单破零策略.md")
    assert os.path.exists(strategy)
    print(f"   ✅ 首单破零策略：{strategy}")

    # 5. 文案四段式
    print("\n[5] 四段式文案校验（案例2）：")
    copy_text = CasePackaging.copy_template(CASES["case2_产品售后知识库"])
    for section in ["项目背景", "项目能力", "项目价值", "适配客户"]:
        assert section in copy_text
        print(f"   ✅ {section}")

    print("\n✅ 零案例破局案例构建测试通过")


if __name__ == "__main__":
    main()
