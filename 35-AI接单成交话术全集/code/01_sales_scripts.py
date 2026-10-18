# 第35篇配套代码：AI接单成交话术全集
# 搞定客户咨询、异议处理、提升转化率
# 运行：python 01_sales_scripts.py

# ========== 各类场景话术 ==========
class SalesScripts:
    """接单成交话术库"""
    
    @staticmethod
    def handle_price_objection():
        """处理价格异议"""
        return [
            {
                "scenario": "客户说太贵",
                "principle": "先确认价值，再谈价格，不要直接降价",
                "scripts": [
                    "理解您的顾虑。这个报价包含了：完整的API集成+知识库搭建+管理后台+部署文档，您可以对比下市场价。",
                    "这样，我先给您做一个基础Demo，您看看效果再说？",
                    "价格可以按功能分期，您先做核心功能，后续再扩展。"
                ]
            },
            {
                "scenario": "客户对比别家",
                "principle": "强调差异化价值和售后服务",
                "scripts": [
                    "确实有便宜的方案，但大多是模板化的。我这边是定制开发，后期扩展灵活，源码全交付。",
                    "低价的通常不包含部署支持和售后维护，我这边提供7天免费维护+30天技术支持。"
                ]
            },
            {
                "scenario": "客户问能不能便宜",
                "principle": "给优惠要换条件",
                "scripts": [
                    "如果您现在确定，可以给个9折优惠。",
                    "如果您帮我介绍一个客户，这次可以优惠500。",
                    "功能上可以精简一下，我先做核心模块，价格能下来不少。"
                ]
            }
        ]
    
    @staticmethod
    def handle_trust_objection():
        """处理信任异议"""
        return [
            {
                "scenario": "客户担心效果",
                "scripts": [
                    "我可以先做一个简单的功能演示，您亲自测试效果，满意再付费。",
                    "这是之前做的项目截图（发图），功能类似的。",
                    "我们可以先签小单，验证效果后再继续。"
                ]
            },
            {
                "scenario": "客户不懂技术",
                "scripts": [
                    "没关系，您只需要告诉我您想实现什么效果，技术方面我来搞定。",
                    "简单说就是：您上传文档，AI就能自动回答您的问题。就这么简单。",
                    "您用微信一样操作就行，不需要任何技术背景。"
                ]
            },
            {
                "scenario": "客户担心售后",
                "scripts": [
                    "交付后7天内任何问题免费处理。",
                    "提供完整的操作手册和部署文档，您团队有人能接手。",
                    "长期合作的话，可以签维护合同，每月固定费用。"
                ]
            }
        ]
    
    @staticmethod
    def handle_decision_objection():
        """处理决策异议"""
        return [
            {
                "scenario": "客户说要考虑",
                "scripts": [
                    "好的，不过有个情况跟您说一下：这个优惠是限时的，本周内确定才能享受。",
                    "您主要考虑哪个方面？是预算还是效果？我可以针对性帮您解决。",
                    "要不我先拉个群，把方案文档发您，您看完再决定？"
                ]
            },
            {
                "scenario": "客户要和别人商量",
                "scripts": [
                    "没问题，要不要我把方案整理成文档，方便您转发给合伙人看？",
                    "方便的话拉个群，我直接给您合伙人讲解一下方案？"
                ]
            }
        ]
    
    @staticmethod
    def closing_techniques():
        """促单技巧"""
        return [
            {
                "technique": "假设成交法",
                "scripts": [
                    "那我们从下周一开始启动，我先拉个群，把需求确认一下？",
                    "我先准备一份详细的方案，您看方便发我邮箱还是微信？"
                ]
            },
            {
                "technique": "二选一法",
                "scripts": [
                    "您看是先做知识库还是先做客服功能？我这边好安排优先级。",
                    "预付款是50%还是30%？两种方式都可以。"
                ]
            },
            {
                "technique": "风险逆转法",
                "scripts": [
                    "我们可以先做一个最小功能版本，您满意了再继续，没有任何风险。",
                    "首单我可以给您一个优惠价，先建立信任。"
                ]
            }
        ]

# ========== 话术练习 ==========
class SalesCoach:
    """话术练习教练"""
    
    def roleplay(self, scenario, customer_says):
        scripts = SalesScripts()
        all_scripts = (
            scripts.handle_price_objection() +
            scripts.handle_trust_objection() +
            scripts.handle_decision_objection()
        )
        
        for s in all_scripts:
            if s["scenario"] in customer_says:
                return s["scripts"][0] if s["scripts"] else "建议根据具体情况调整话术"
        
        return "感谢咨询！方便说下您的具体需求吗？我免费出方案和报价。"

if __name__ == "__main__":
    print("=" * 60)
    print("💬 AI接单成交话术全集")
    print("=" * 60)
    
    scripts = SalesScripts()
    
    print("\n💰 价格异议处理")
    print("-" * 50)
    for item in scripts.handle_price_objection():
        print(f"\n场景：{item['scenario']}")
        print(f"原则：{item['principle']}")
        for s in item['scripts']:
            print(f"  💡 {s}")
    
    print("\n🤝 信任异议处理")
    print("-" * 50)
    for item in scripts.handle_trust_objection():
        print(f"\n场景：{item['scenario']}")
        for s in item['scripts']:
            print(f"  💡 {s}")
    
    print("\n⏳ 决策异议处理")
    print("-" * 50)
    for item in scripts.handle_decision_objection():
        print(f"\n场景：{item['scenario']}")
        for s in item['scripts']:
            print(f"  💡 {s}")
    
    print("\n🎯 促单技巧")
    print("-" * 50)
    for item in scripts.closing_techniques():
        print(f"\n技巧：{item['technique']}")
        for s in item['scripts']:
            print(f"  💡 {s}")
    
    print("\n" + "=" * 60)
    print("🤖 话术练习模式")
    print("=" * 60)
    coach = SalesCoach()
    test_cases = [
        "太贵了，能便宜点吗？",
        "你们做过类似项目吗？效果怎么样？",
        "我要考虑考虑"
    ]
    for case in test_cases:
        print(f"\n客户：{case}")
        print(f"回复：{coach.roleplay('通用', case)}")
