# 第32篇配套代码：标准化交付文档+售后方案
# 生成标准化的项目交付文档模板
# 运行：python 01_delivery_template.py

import json
from datetime import datetime, timedelta

# ========== 项目交付文档模板 ==========
class ProjectDeliverable:
    """项目交付文档生成器"""
    
    @staticmethod
    def generate_handover_doc(project_name, customer, tech_stack, features):
        doc = f"""
# {project_name} 项目交付说明书

## 基本信息
- 项目名称：{project_name}
- 客户：{customer}
- 交付日期：{datetime.now().strftime('%Y-%m-%d')}
- 技术栈：{', '.join(tech_stack)}

## 功能清单
"""
        for i, feat in enumerate(features, 1):
            doc += f"{i}. ✅ {feat}\n"

        doc += """
## 部署说明
1. 环境要求：Python 3.10+ / Node.js 18+ / Docker
2. 启动命令：详见 README.md
3. 配置文件：复制 .env.example 为 .env 并填入密钥

## 使用指南
1. 访问 http://localhost:8000 进入管理后台
2. 使用管理员账号登录（初始密码请在部署后修改）
3. 按照说明文档配置知识库/模型参数

## 售后支持
- 文档地址：https://docs.example.com
- 技术支持微信：[请填写]
- 响应时间：工作日 4 小时内

## 验收清单
- [ ] 所有功能正常使用
- [ ] API接口可正常调用
- [ ] 数据备份策略已配置
- [ ] 日志记录正常运行
- [ ] 权限管理已配置
"""
        return doc

# ========== 售后运维方案 ==========
class AfterSalePlan:
    """售后运维方案"""
    
    def __init__(self, project_name):
        self.project_name = project_name
        self.tickets = []
    
    def create_maintenance_plan(self):
        return {
            "日常维护": [
                "每日检查服务状态",
                "监控API调用量",
                "检查日志异常"
            ],
            "周度维护": [
                "数据库备份检查",
                "磁盘空间清理",
                "模型调用统计"
            ],
            "月度维护": [
                "知识库更新优化",
                "性能评估报告",
                "安全漏洞扫描"
            ]
        }
    
    def create_service_level_agreement(self):
        return {
            "响应时间": "工作时间4小时 / 非工作时间12小时",
            "故障等级": {
                "P0-系统崩溃": "30分钟内响应，2小时修复",
                "P1-功能异常": "2小时内响应，8小时修复",
                "P2-体验优化": "24小时内响应，下个版本修复"
            },
            "服务范围": [
                "系统故障排查与修复",
                "知识库内容更新",
                "模型调优建议",
                "安全更新部署"
            ]
        }
    
    def add_ticket(self, customer, issue, level="P2"):
        ticket = {
            "id": f"TICKET-{datetime.now().strftime('%Y%m%d')}-{len(self.tickets)+1:03d}",
            "customer": customer,
            "issue": issue,
            "level": level,
            "status": "open",
            "created": datetime.now().isoformat()
        }
        self.tickets.append(ticket)
        return ticket

# ========== 模板使用示例 ==========
if __name__ == "__main__":
    print("=" * 60)
    print("📋 标准化项目交付文档模板")
    print("=" * 60)
    
    doc = ProjectDeliverable.generate_handover_doc(
        project_name="企业智能客服Agent",
        customer="XX科技有限公司",
        tech_stack=["Python", "FastAPI", "OpenAI", "ChromaDB"],
        features=[
            "智能问答：基于RAG的私有知识库问答",
            "多轮对话：支持上下文记忆与连续对话",
            "工具调用：查天气、计算器、搜索",
            "管理后台：知识库管理与监控面板",
            "API接口：标准化RESTful API"
        ]
    )
    print(doc)
    
    print("\n" + "=" * 60)
    print("🔧 售后运维方案")
    print("=" * 60)
    plan = AfterSalePlan("企业智能客服Agent")
    maintenance = plan.create_maintenance_plan()
    for period, tasks in maintenance.items():
        print(f"\n{period}：")
        for t in tasks:
            print(f"  • {t}")
    
    print("\n" + "=" * 60)
    print("📄 服务等级协议（SLA）")
    print("=" * 60)
    sla = plan.create_service_level_agreement()
    print(f"\n响应时间：{sla['响应时间']}")
    for level, time in sla['故障等级'].items():
        print(f"  {level}：{time}")
    
    print("\n工单示例：")
    ticket = plan.add_ticket("XX科技", "知识库问答返回结果为空", "P1")
    print(f"  📌 {ticket['id']} | {ticket['issue']} | {ticket['level']} | 状态：{ticket['status']}")
