# 第33篇配套代码：零案例新手破局
# 从零开始获取第一个AI接单项目的完整方案
# 运行：python 01_breakthrough_plan.py

# ========== 新手破局路线图 ==========
class BeginnerBreakthrough:
    """零案例新手破局方案"""
    
    def __init__(self):
        self.skills = []
        self.portfolio_items = []
        self.client_leads = []
    
    def skill_assessment(self):
        """技能自评与学习路径"""
        return {
            "必备技能": [
                {"name": "Python基础", "level": "入门", "time": "1周"},
                {"name": "OpenAI API调用", "level": "入门", "time": "3天"},
                {"name": "FastAPI部署", "level": "入门", "time": "3天"},
                {"name": "基础Prompt工程", "level": "入门", "time": "2天"}
            ],
            "核心技能（1个月掌握）": [
                "RAG知识库搭建",
                "Agent工具调用",
                "基础前端对话界面"
            ],
            "加分技能": [
                "Linux服务器部署",
                "Docker容器化",
                "ChromaDB向量库"
            ]
        }
    
    def build_portfolio(self):
        """零成本作品集构建方案"""
        return [
            {
                "project": "智能客服Demo",
                "type": "开源项目 + 录屏演示",
                "platform": "GitHub + B站",
                "time": "3天",
                "description": "用FastAPI+OpenAI搭建一个基础问答API，录制演示视频"
            },
            {
                "project": "个人知识库助手",
                "type": "在线体验链接",
                "platform": "HuggingFace Spaces",
                "time": "5天",
                "description": "部署一个RAG知识库问答系统到免费服务器"
            },
            {
                "project": "自动化办公工具",
                "type": "工具截图 + 功能说明",
                "platform": "知乎/小红书",
                "time": "4天",
                "description": "做一个文件批量处理工具，展示效果对比"
            }
        ]
    
    def find_first_client(self):
        """获取第一单的渠道和策略"""
        return {
            "渠道": [
                {"name": "闲鱼", "strategy": "低价挂服务，积累评价", "expected_time": "1-7天"},
                {"name": "知乎", "strategy": "回答AI相关问题，展示专业能力", "expected_time": "7-14天"},
                {"name": "朋友圈/社群", "strategy": "告知朋友自己在做AI开发", "expected_time": "1-30天"},
                {"name": "猪八戒/一品威客", "strategy": "关注AI相关需求，低价竞标", "expected_time": "7-30天"},
                {"name": "线下破局", "strategy": "去创业园区/科技公司发名片", "expected_time": "14-60天"}
            ],
            "报价策略": [
                "第一单：500-2000元（积累案例和口碑）",
                "第二单：2000-5000元（有案例支撑）",
                "第三单起：5000+元（正常市场价）"
            ]
        }
    
    def sales_script(self):
        """新手接单话术模板"""
        return """
【破局话术模板】

客户：你能做AI客服吗？
你：可以的，我最近刚完成一个类似的项目（展示Demo）。
客户有案例吗？
你：这是我做的演示项目（发链接/视频），功能包括XYZ。
客户：多少钱？
你：这个要看具体需求，您可以先说说您的想法，我给您做个评估。
（重点：先聊需求，再报价，不要先报价再聊需求）

客户：不太放心
你：我们可以先做一个小功能验证，您满意再继续。
（降低门槛，用"先做后付"建立信任）
"""

# ========== 执行计划 ==========
if __name__ == "__main__":
    bt = BeginnerBreakthrough()
    
    print("=" * 60)
    print("🚀 零案例新手破局 - 30天行动路线图")
    print("=" * 60)
    
    print("\n📚 第一阶段：技能储备（第1-7天）")
    skills = bt.skill_assessment()
    print("  必备技能：")
    for s in skills["必备技能"]:
        print(f"    • {s['name']}（{s['level']}，{s['time']}）")
    
    print("\n🛠️ 第二阶段：作品集构建（第8-20天）")
    portfolio = bt.build_portfolio()
    for item in portfolio:
        print(f"  📌 {item['project']}")
        print(f"    平台：{item['platform']} | 时间：{item['time']}")
        print(f"    说明：{item['description']}")
    
    print("\n🤝 第三阶段：第一单获取（第21-30天）")
    channels = bt.find_first_client()
    print("  渠道策略：")
    for ch in channels["渠道"]:
        print(f"    • {ch['name']}：{ch['strategy']}（预计{ch['expected_time']}）")
    
    print("\n报价策略：")
    for p in channels["报价策略"]:
        print(f"    • {p}")
    
    print("\n💬 话术模板：")
    print(bt.sales_script())
