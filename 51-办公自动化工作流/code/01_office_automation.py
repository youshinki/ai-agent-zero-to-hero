# 第51篇配套代码：办公自动化工作流
# 职场刚需副业变现赛道
# 运行：python 01_office_automation.py

import csv
import json
from datetime import datetime

# ========== 办公自动化工作流 ==========
class OfficeAutomation:
    """办公自动化工作流引擎"""
    
    def __init__(self):
        self.workflows = {}
        self.scheduled_tasks = []
    
    def create_report(self, title, sections):
        """自动生成报告"""
        report = f"# {title}\n\n"
        report += f"生成日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        for section in sections:
            report += f"## {section['title']}\n"
            report += f"{section['content']}\n\n"
        
        return report
    
    def process_excel(self, data, operations):
        """处理Excel数据"""
        results = []
        for row in data:
            processed_row = {}
            for op in operations:
                if op["type"] == "sum":
                    processed_row[op["name"]] = sum(row.get(k, 0) for k in op["columns"])
                elif op["type"] == "avg":
                    vals = [row.get(k, 0) for k in op["columns"]]
                    processed_row[op["name"]] = sum(vals) / len(vals) if vals else 0
                elif op["type"] == "concat":
                    parts = [str(row.get(k, "")) for k in op["columns"]]
                    processed_row[op["name"]] = " ".join(parts)
            results.append(processed_row)
        return results
    
    def batch_rename(self, files, pattern):
        """批量重命名（模拟）"""
        renamed = []
        for i, f in enumerate(files):
            new_name = pattern.replace("{num}", str(i+1)).replace("{name}", f)
            renamed.append({"old": f, "new": new_name})
        return renamed
    
    def extract_data(self, text, pattern):
        """从文本提取结构化数据"""
        import re
        results = {}
        for key, regex in pattern.items():
            match = re.search(regex, text)
            if match:
                results[key] = match.group(1)
        return results
    
    def send_emails(self, recipients, template, data):
        """批量发送邮件（模拟）"""
        sent = []
        for recipient in recipients:
            email_body = template.format(**data, **recipient)
            sent.append({
                "to": recipient["email"],
                "subject": f"办公自动化通知 - {recipient['name']}",
                "body": email_body
            })
        return sent

# ========== 工作流模板 ==========
class WorkflowTemplates:
    """工作流模板库"""
    
    @staticmethod
    def weekly_report_template():
        return {
            "name": "周报自动生成",
            "steps": [
                "从数据库读取本周数据",
                "统计各维度指标",
                "生成周报文档",
                "发送给相关人"
            ],
            "output": "周报.docx"
        }
    
    @staticmethod
    def data_cleaning_template():
        return {
            "name": "数据清洗工作流",
            "steps": [
                "读取原始数据文件",
                "去除重复行",
                "填充缺失值",
                "格式标准化",
                "输出清洗后文件"
            ],
            "output": "cleaned_data.csv"
        }

# ========== 客户案例 ==========
class UseCases:
    """办公自动化案例库"""
    
    @staticmethod
    def get_cases():
        return [
            {
                "name": "自动生成销售周报",
                "pain_point": "每周手动整理销售数据、写周报耗时2小时",
                "solution": "自动化读取CRM数据，自动生成图表+文字分析",
                "result": "耗时从2小时降到5分钟",
                "price": "5000元"
            },
            {
                "name": "批量处理合同",
                "pain_point": "每天手动处理50+份合同录入",
                "solution": "OCR识别+自动提取关键字段+录入系统",
                "result": "效率提升20倍，错误率降为0",
                "price": "8000元"
            },
            {
                "name": "自动邮件回复",
                "pain_point": "客服人员每天回复200+封重复邮件",
                "solution": "AI自动分类+智能回复模板+人工审核",
                "result": "自动处理80%的邮件",
                "price": "12000元"
            }
        ]

if __name__ == "__main__":
    print("=" * 60)
    print("🏢 办公自动化工作流")
    print("=" * 60)
    
    oa = OfficeAutomation()
    
    print("\n1️⃣ 自动生成报告")
    print("-" * 40)
    report = oa.create_report("2024年1月销售周报", [
        {"title": "销售概况", "content": "本周总销售额：100,000元，同比增长20%"},
        {"title": "重点客户", "content": "新增3个重点客户，预计带来50,000元收入"},
        {"title": "下周计划", "content": "重点跟进A、B两个潜在客户"}
    ])
    print(report[:300] + "...")
    
    print("\n2️⃣ 数据处理")
    print("-" * 40)
    data = [
        {"name": "张三", "sales_1": 100, "sales_2": 200, "sales_3": 150},
        {"name": "李四", "sales_1": 300, "sales_2": 250, "sales_3": 400},
    ]
    operations = [
        {"type": "sum", "name": "total_sales", "columns": ["sales_1", "sales_2", "sales_3"]},
        {"type": "avg", "name": "avg_sales", "columns": ["sales_1", "sales_2", "sales_3"]}
    ]
    results = oa.process_excel(data, operations)
    for r in results:
        print(f"  {r}")
    
    print("\n3️⃣ 批量重命名")
    files = ["report_v1.docx", "report_v2.docx", "report_v3.docx"]
    renamed = oa.batch_rename(files, "{num}_{name}")
    for r in renamed:
        print(f"  {r['old']} → {r['new']}")
    
    print("\n4️⃣ 数据提取")
    text = "联系人：张三，电话：13800138000，邮箱：zhang@example.com"
    pattern = {"name": r"联系人：(\w+)", "phone": r"电话：(\d+)", "email": r"邮箱：(\S+)"}
    extracted = oa.extract_data(text, pattern)
    print(f"  提取结果：{extracted}")
    
    print("\n5️⃣ 客户案例")
    print("-" * 40)
    for case in UseCases.get_cases():
        print(f"\n  📌 {case['name']}")
        print(f"    痛点：{case['pain_point']}")
        print(f"    方案：{case['solution']}")
        print(f"    效果：{case['result']}")
        print(f"    报价：{case['price']}")
