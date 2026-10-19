#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第51篇配套完整项目代码 · office_automation.py
赛道6：办公自动化工作流（职场刚需副业变现）

  1. 自动报告生成（周报/月报）
  2. 表格数据处理（统计/清洗/汇总）
  3. 批量文件重命名
  4. 文本结构化提取
  5. 邮件批量生成
  6. 工作流模板与客户案例

运行: python office_automation.py
"""

import csv
import io
import os
import re
from datetime import datetime
from typing import Dict, List


# ======================================================================
# 一、自动报告生成
# ======================================================================

def generate_report(title: str, sections: List[Dict], output_dir: str = "output") -> str:
    """生成 Markdown 报告"""
    os.makedirs(output_dir, exist_ok=True)
    lines = [f"# {title}", "",
             f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    for sec in sections:
        lines.append(f"## {sec['title']}")
        lines.append(sec["content"])
        lines.append("")
    content = "\n".join(lines)
    safe = re.sub(r"[\\/:*?\"<>|]", "_", title)
    path = os.path.join(output_dir, f"{safe}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ======================================================================
# 二、表格数据处理
# ======================================================================

def process_table(rows: List[Dict], operations: List[Dict]) -> List[Dict]:
    """对表格数据做聚合/计算"""
    out = []
    for row in rows:
        item = dict(row)
        for op in operations:
            cols = op["columns"]
            values = []
            for c in cols:
                try:
                    values.append(float(row.get(c, 0)))
                except (TypeError, ValueError):
                    values.append(0.0)
            if op["type"] == "sum":
                item[op["name"]] = round(sum(values), 2)
            elif op["type"] == "avg":
                item[op["name"]] = round(sum(values) / len(values), 2) if values else 0
            elif op["type"] == "max":
                item[op["name"]] = max(values) if values else 0
            elif op["type"] == "concat":
                item[op["name"]] = " ".join(str(row.get(c, "")) for c in cols)
        out.append(item)
    return out


def to_csv(rows: List[Dict]) -> str:
    if not rows:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


# ======================================================================
# 三、批量重命名
# ======================================================================

def batch_rename(files: List[str], pattern: str, dry_run: bool = True) -> List[Dict]:
    """批量重命名（默认演练不落盘）"""
    results = []
    for i, name in enumerate(files, 1):
        new = pattern.replace("{num:02d}", f"{i:02d}").replace("{num}", str(i))
        new = new.replace("{name}", name)
        results.append({"old": name, "new": new})
        if not dry_run:
            # 实际项目用 os.rename(os.path.join(dir, old), ...)
            pass
    return results


# ======================================================================
# 四、文本结构化提取
# ======================================================================

def extract_fields(text: str, patterns: Dict[str, str]) -> Dict[str, str]:
    out = {}
    for key, pattern in patterns.items():
        m = re.search(pattern, text)
        out[key] = m.group(1).strip() if m else ""
    return out


# ======================================================================
# 五、邮件批量生成
# ======================================================================

def generate_emails(recipients: List[Dict], subject_tpl: str,
                    body_tpl: str) -> List[Dict]:
    mails = []
    for r in recipients:
        mails.append({
            "to": r["email"],
            "subject": subject_tpl.format(**r),
            "body": body_tpl.format(**r),
        })
    return mails


# ======================================================================
# 六、工作流模板与案例
# ======================================================================

WORKFLOW_TEMPLATES = {
    "周报自动生成": ["读取本周数据", "统计指标", "生成报告", "发送邮件"],
    "数据清洗": ["读取原始数据", "去重", "填充缺失", "格式标准化", "导出"],
    "合同批量处理": ["OCR识别", "提取关键字段", "录入系统", "生成台账"],
}

CASE_LIBRARY = [
    {"name": "自动生成销售周报", "pain": "每周手动整理2小时",
     "solution": "自动读CRM→汇总→生成报告", "result": "2小时→5分钟", "price": 3000},
    {"name": "批量处理合同", "pain": "每天手动录入50+份",
     "solution": "OCR+字段提取+自动录入", "result": "效率20倍，0错误", "price": 8000},
    {"name": "自动邮件回复", "pain": "客服每天回复200+封",
     "solution": "AI分类+模板回复+人工审核", "result": "自动处理80%", "price": 12000},
]


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("🏢 赛道6：办公自动化工作流 · 演示")
    print("=" * 66)
    
    # 1. 报告
    print("\n[1] 自动生成周报：")
    path = generate_report("2024年第1周销售周报", [
        {"title": "一、整体业绩", "content": "总销售额 120 万元，同比增长 15%，完成目标 108%。"},
        {"title": "二、重点客户", "content": "新增 3 个重点客户，预计带来 50 万元收入。"},
        {"title": "三、问题与计划", "content": "交付周期偏长，下周推行标准化交付模板。"},
    ])
    print(f"   ✅ 已生成：{path}")
    
    # 2. 表格处理
    print("\n[2] 表格数据处理：")
    rows = [
        {"name": "张三", "m1": 100, "m2": 200, "m3": 150},
        {"name": "李四", "m1": 300, "m2": 250, "m3": 400},
    ]
    out = process_table(rows, [
        {"type": "sum", "name": "total", "columns": ["m1", "m2", "m3"]},
        {"type": "avg", "name": "avg", "columns": ["m1", "m2", "m3"]},
    ])
    for r in out:
        print(f"   {r['name']}：总额{r['total']}，均值{r['avg']}")
    print(f"   CSV预览：{to_csv(out).splitlines()[0]}")
    
    # 3. 批量重命名
    print("\n[3] 批量重命名：")
    files = ["报告_v1.docx", "报告_v2.docx", "报告_final.docx"]
    for r in batch_rename(files, "{num:02d}_{name}"):
        print(f"   {r['old']} → {r['new']}")
    
    # 4. 字段提取
    print("\n[4] 文本结构化提取：")
    text = "联系人：张三，电话：13800138000，邮箱：zhang@example.com，金额：5000元"
    fields = extract_fields(text, {
        "姓名": r"联系人：(\w+)",
        "电话": r"电话：(\d+)",
        "邮箱": r"邮箱：([\w.@-]+)",
        "金额": r"金额：(\d+)元",
    })
    print(f"   {fields}")
    
    # 5. 邮件
    print("\n[5] 批量邮件：")
    mails = generate_emails(
        [{"name": "张三", "email": "z@example.com"},
         {"name": "李四", "email": "l@example.com"}],
        "【周报】{name} 本周工作总结",
        "{name} 您好，本周周报已生成，请查收。",
    )
    for m in mails:
        print(f"   {m['to']}｜{m['subject']}")
    
    # 6. 模板与案例
    print("\n[6] 工作流模板：")
    for name, steps in WORKFLOW_TEMPLATES.items():
        print(f"   {name}：{' → '.join(steps)}")
    print("\n[7] 客户案例：")
    for c in CASE_LIBRARY:
        print(f"   {c['name']}：{c['result']}（报价¥{c['price']}）")


if __name__ == "__main__":
    demo()
