#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第51篇配套 · test_office_automation.py
验证：报告/表格/重命名/字段提取/邮件/模板案例

运行: python test_office_automation.py
"""

import os
import shutil

from office_automation import (
    generate_report, process_table, to_csv, batch_rename,
    extract_fields, generate_emails, WORKFLOW_TEMPLATES,
    CASE_LIBRARY, demo,
)


def main():
    print("=" * 66)
    print("🧪 办公自动化工作流测试")
    print("=" * 66)

    shutil.rmtree("output", ignore_errors=True)

    # 1. 报告
    print("\n[1] 自动报告：")
    path = generate_report("测试报告", [
        {"title": "一、概况", "content": "内容A"},
        {"title": "二、计划", "content": "内容B"},
    ])
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "测试报告" in content and "内容A" in content
    print(f"   ✅ {path}")

    # 2. 表格
    print("\n[2] 表格处理：")
    rows = [{"name": "A", "x": 10, "y": 20}, {"name": "B", "x": 30, "y": 40}]
    out = process_table(rows, [
        {"type": "sum", "name": "total", "columns": ["x", "y"]},
        {"type": "max", "name": "max", "columns": ["x", "y"]},
    ])
    assert out[0]["total"] == 30 and out[1]["max"] == 40
    csv_text = to_csv(out)
    assert "total" in csv_text and "A" in csv_text
    print(f"   {out[0]}")
    print(f"   CSV行数：{len(csv_text.splitlines())}")

    # 3. 重命名
    print("\n[3] 批量重命名：")
    renamed = batch_rename(["a.txt", "b.txt"], "{num:02d}_{name}")
    assert renamed[0]["new"] == "01_a.txt"
    for r in renamed:
        print(f"   {r['old']} → {r['new']}")

    # 4. 字段提取
    print("\n[4] 字段提取：")
    text = "联系人：张三，电话：13800138000，金额：5000元"
    fields = extract_fields(text, {
        "姓名": r"联系人：(\w+)", "电话": r"电话：(\d+)", "金额": r"金额：(\d+)",
    })
    assert fields["姓名"] == "张三" and fields["电话"] == "13800138000"
    print(f"   {fields}")

    # 5. 邮件
    print("\n[5] 批量邮件：")
    mails = generate_emails(
        [{"name": "张三", "email": "z@x.com"}],
        "【周报】{name}", "{name} 您好，请查收。",
    )
    assert mails[0]["subject"] == "【周报】张三"
    print(f"   {mails[0]['subject']} → {mails[0]['to']}")

    # 6. 模板与案例
    print(f"\n[6] 工作流模板：{len(WORKFLOW_TEMPLATES)} 个")
    print(f"   客户案例：{len(CASE_LIBRARY)} 个")
    assert len(WORKFLOW_TEMPLATES) == 3 and len(CASE_LIBRARY) == 3

    print("\n[7] 完整演示：")
    demo()

    print("\n✅ 办公自动化工作流测试通过")


if __name__ == "__main__":
    main()
