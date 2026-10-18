# 第37篇配套代码：项目分级与报价体系搭建
# 精准定价、利润最大化
# 运行：python 01_pricing_system.py

# ========== 项目分级标准 ==========
class ProjectTier:
    """项目分级与报价方案"""
    
    TIERS = {
        "S级-复杂企业项目": {
            "price_range": "30000-100000+",
            "timeline": "30-60天",
            "features": [
                "多Agent协作系统",
                "私有化部署（内网/本地）",
                "多租户权限管理",
                "定制化UI界面",
                "第三方系统集成",
                "7×24运维支持"
            ],
            "target_clients": "中型企业、上市公司、政府单位"
        },
        "A级-标准企业项目": {
            "price_range": "10000-30000",
            "timeline": "15-30天",
            "features": [
                "RAG知识库问答系统",
                "OpenAI/本地模型接入",
                "管理后台",
                "API接口封装",
                "基础权限管理",
                "部署文档+运维手册"
            ],
            "target_clients": "小微企业、创业公司、部门级需求"
        },
        "B级-个人/工作室项目": {
            "price_range": "3000-10000",
            "timeline": "7-15天",
            "features": [
                "单Agent功能开发",
                "基础对话界面",
                "简单知识库",
                "工具调用集成",
                "基础文档"
            ],
            "target_clients": "个人开发者、小工作室、自媒体"
        },
        "C级-轻量任务": {
            "price_range": "500-3000",
            "timeline": "1-7天",
            "features": [
                "API对接",
                "简单Prompt调优",
                "基础脚本开发",
                "配置调试"
            ],
            "target_clients": "个人用户、初次合作客户"
        }
    }
    
    @staticmethod
    def recommend_tier(budget, complexity, timeline_days):
        """根据客户情况推荐项目等级"""
        score = 0
        if budget >= 30000: score += 4
        elif budget >= 10000: score += 3
        elif budget >= 3000: score += 2
        else: score += 1
        
        if complexity >= 8: score += 3
        elif complexity >= 5: score += 2
        else: score += 1
        
        if timeline_days >= 30: score += 2
        elif timeline_days >= 15: score += 1
        
        if score >= 8: return "S级-复杂企业项目"
        elif score >= 6: return "A级-标准企业项目"
        elif score >= 4: return "B级-个人/工作室项目"
        else: return "C级-轻量任务"
    
    @staticmethod
    def calculate_price(tier, addons):
        """计算报价（基础价 + 附加功能）"""
        base_prices = {
            "S级-复杂企业项目": 50000,
            "A级-标准企业项目": 18000,
            "B级-个人/工作室项目": 6000,
            "C级-轻量任务": 1500
        }
        
        addon_prices = {
            "多模型接入": 3000,
            "管理后台": 5000,
            "私有化部署": 8000,
            "API封装": 2000,
            "运维支持1个月": 3000,
            "定制UI": 5000,
            "多语言支持": 2000
        }
        
        total = base_prices.get(tier, 1000)
        for addon in addons:
            total += addon_prices.get(addon, 0)
        
        return total

# ========== 成本核算 ==========
class CostCalculator:
    """成本计算器"""
    
    @staticmethod
    def estimate_cost(tier, work_days, model_cost_per_month=500):
        """估算项目成本"""
        hourly_rate = 100  # 时薪
        dev_cost = work_days * 8 * hourly_rate
        model_cost = model_cost_per_month * 2  # 2个月
        misc_cost = dev_cost * 0.15  # 杂项15%
        
        return {
            "开发成本": dev_cost,
            "模型调用成本": model_cost,
            "杂项(服务器/域名等)": misc_cost,
            "总成本": dev_cost + model_cost + misc_cost,
            "建议报价(min)": int((dev_cost + model_cost + misc_cost) * 2),
            "建议报价(max)": int((dev_cost + model_cost + misc_cost) * 3.5)
        }

if __name__ == "__main__":
    print("=" * 60)
    print("📊 项目分级与报价体系")
    print("=" * 60)
    
    print("\n📋 项目分级标准")
    print("-" * 40)
    for tier, info in ProjectTier.TIERS.items():
        print(f"\n🔷 {tier}")
        print(f"  报价范围：{info['price_range']}")
        print(f"  周期：{info['timeline']}")
        print(f"  目标客户：{info['target_clients']}")
        print("  包含功能：")
        for f in info['features']:
            print(f"    • {f}")
    
    print("\n🎯 推荐测试")
    print("-" * 40)
    test_cases = [
        ("中小企业知识库", 15000, 7, 20),
        ("个人AI助手", 5000, 4, 10),
        ("大企业多Agent系统", 50000, 9, 45)
    ]
    for name, budget, complexity, days in test_cases:
        tier = ProjectTier.recommend_tier(budget, complexity, days)
        price = ProjectTier.calculate_price(tier, ["管理后台", "API封装"])
        print(f"  {name}（预算{budget}）→ {tier} → 建议报价：{price}元")
    
    print("\n💰 成本核算示例")
    print("-" * 40)
    cost = CostCalculator.estimate_cost("A级-标准企业项目", 20)
    for item, amount in cost.items():
        print(f"  {item}：{amount}元")
