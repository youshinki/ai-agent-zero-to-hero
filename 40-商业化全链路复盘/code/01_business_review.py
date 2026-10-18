# 第40篇配套代码：商业化全链路复盘
# AI Agent接单生意的全链路复盘与优化
# 运行：python 01_business_review.py

# ========== 全链路数据复盘 ==========
class BusinessReview:
    """商业化全链路复盘"""
    
    def __init__(self):
        self.projects = []
        self.revenue = 0
        self.costs = 0
        self.leads = []
    
    def add_project(self, name, tier, revenue, cost, satisfaction):
        self.projects.append({
            "name": name, "tier": tier,
            "revenue": revenue, "cost": cost,
            "profit": revenue - cost,
            "margin": round((revenue - cost) / revenue * 100, 1),
            "satisfaction": satisfaction
        })
        self.revenue += revenue
        self.costs += cost
    
    def get_metrics(self):
        total_profit = self.revenue - self.costs
        avg_margin = round(total_profit / self.revenue * 100, 1) if self.revenue else 0
        return {
            "总项目数": len(self.projects),
            "总收入": self.revenue,
            "总成本": self.costs,
            "总利润": total_profit,
            "平均利润率": f"{avg_margin}%",
            "平均客单价": round(self.revenue / len(self.projects), 0) if self.projects else 0
        }
    
    def get_channel_roi(self):
        """各渠道ROI分析"""
        return {
            "闲鱼": {"投入": 0, "获客": 15, "roi": "∞（零成本）"},
            "知乎": {"投入": 500, "获客": 8, "roi": "1600%"},
            "小红书": {"投入": 300, "获客": 5, "roi": "1667%"},
            "私域转介绍": {"投入": 0, "获客": 10, "roi": "∞（零成本）"},
            "猪八戒": {"投入": 1000, "获客": 3, "roi": "300%"}
        }

# ========== 客户终身价值计算 ==========
class CLVCalculator:
    """客户终身价值计算"""
    
    @staticmethod
    def calculate_clv(initial_order, monthly_maintenance, months, referral_prob=0.2):
        """计算客户终身价值"""
        initial_revenue = initial_order
        maintenance_revenue = monthly_maintenance * months
        referral_revenue = initial_revenue * referral_prob
        total = initial_revenue + maintenance_revenue + referral_revenue
        
        return {
            "首单收入": initial_revenue,
            "维护收入": maintenance_revenue,
            "推荐收入": referral_revenue,
            "CLV": total,
            "占比": f"{'首单'}:{initial_revenue/total*100:.0f}% | {'维护'}:{maintenance_revenue/total*100:.0f}% | {'推荐'}:{referral_revenue/total*100:.0f}%"
        }

# ========== 复盘报告 ==========
class ReviewReport:
    """复盘报告生成器"""
    
    @staticmethod
    def generate(review, clv):
        report = f"""
# AI Agent 接单生意 - 全链路复盘报告

## 一、经营概况
- 累计完成项目：{review.get_metrics()['总项目数']}个
- 总收入：¥{review.get_metrics()['总收入']:,}
- 总成本：¥{review.get_metrics()['总成本']:,}
- 总利润：¥{review.get_metrics()['总利润']:,}
- 平均利润率：{review.get_metrics()['平均利润率']}

## 二、项目分布
"""
        for p in review.projects:
            report += f"- {p['name']} | {p['tier']} | 收入¥{p['revenue']:,} | 利润¥{p['profit']:,} | 利润率{p['margin']}% | 满意度{p['satisfaction']}/5\n"
        
        report += f"""
## 三、客户终身价值
- 平均CLV：¥{clv['CLV']:,}
- 维护收入占比：{(clv['maintenance_revenue']/clv['CLV']*100):.0f}%
- 推荐收入占比：{(clv['referral_revenue']/clv['CLV']*100):.0f}%

## 四、关键结论
1. 高客单价项目利润率高，但获客周期长
2. 运维托管收入是长期稳定现金流
3. 老客户推荐是最高效的获客渠道
4. 技术壁垒决定溢价空间
"""
        return report

if __name__ == "__main__":
    print("=" * 60)
    print("📊 商业化全链路复盘")
    print("=" * 60)
    
    review = BusinessReview()
    review.add_project("企业客服Agent", "A级", 18000, 6000, 5)
    review.add_project("个人知识库", "B级", 6000, 2000, 4)
    review.add_project("办公自动化", "B级", 8000, 3000, 5)
    review.add_project("小企业RAG", "A级", 15000, 5000, 4)
    review.add_project("API对接调试", "C级", 2000, 500, 4)
    
    print("\n📈 经营数据")
    print("-" * 40)
    for k, v in review.get_metrics().items():
        print(f"  {k}：{v}")
    
    print("\n📊 各项目详情")
    print("-" * 40)
    for p in review.projects:
        print(f"  {p['name']} | {p['tier']} | 利润¥{p['profit']:,} | 利润率{p['margin']}%")
    
    print("\n📱 渠道ROI分析")
    print("-" * 40)
    for channel, data in review.get_channel_roi().items():
        print(f"  {channel}：投入¥{data['投入']} → 获客{data['获客']}人 → ROI {data['roi']}")
    
    print("\n💰 客户终身价值")
    print("-" * 40)
    clv = CLVCalculator.calculate_clv(initial_order=15000, monthly_maintenance=3000, months=12)
    for k, v in clv.items():
        print(f"  {k}：¥{v:,}" if isinstance(v, (int, float)) else f"  {k}：{v}")
    
    print("\n" + "=" * 60)
    print("📋 复盘报告")
    print("=" * 60)
    print(ReviewReport.generate(review, clv))
