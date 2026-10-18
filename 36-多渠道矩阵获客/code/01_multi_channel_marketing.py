# 第36篇配套代码：多渠道矩阵获客
# B站/小红书/私域联动放大接单量
# 运行：python 01_multi_channel_marketing.py

# ========== 各平台内容策略 ==========
class ChannelStrategy:
    """多渠道内容策略"""
    
    @staticmethod
    def bilibili_strategy():
        return {
            "平台特征": "长视频、技术深度内容、年轻用户",
            "内容方向": [
                {"title": "【手把手】30分钟搭建自己的AI智能体", "type": "教程"},
                {"title": "我用AI自动写周报，老板以为我开挂了", "type": "效果展示"},
                {"title": "AI接单3个月赚了X万，真实经验分享", "type": "经验"},
                {"title": "普通人如何用AI开发副业赚钱", "type": "干货"}
            ],
            "发布频率": "每周2-3条",
            "引流方式": "视频简介留公众号/私信获取工具包",
            "变现路径": "视频引流 → 私域转化 → 接单"
        }
    
    @staticmethod
    def xiaohongshu_strategy():
        return {
            "平台特征": "图文、种草、女性用户多、决策力强",
            "内容方向": [
                {"title": "打工人必备的5个AI工具", "type": "工具推荐"},
                {"title": "AI做PPT有多离谱？我试了试...", "type": "体验分享"},
                {"title": "从0开始做AI副业，我做了什么", "type": "经验"},
                {"title": "用AI一天做了10篇小红书文案", "type": "效果展示"}
            ],
            "发布频率": "每天1条",
            "引流方式": "评论区引导、主页挂微信",
            "变现路径": "种草 → 专业形象 → 咨询 → 接单"
        }
    
    @staticmethod
    def wechat_private_domain():
        return {
            "运营方式": [
                "朋友圈每天发1-2条案例/干货",
                "微信群分享AI工具使用技巧",
                "公众号发深度技术文章",
                "私聊维护核心客户"
            ],
            "朋友圈内容计划": {
                "周一": "客户案例展示（打码保护隐私）",
                "周二": "AI工具推荐/使用技巧",
                "周三": "行业动态/技术分享",
                "周四": "客户好评截图",
                "周五": "周末福利/小工具免费送",
                "周末": "个人思考/生活内容（拉近距离）"
            },
            "变现路径": "信任建立 → 需求挖掘 → 方案定制 → 成交"
        }

# ========== 内容排期与自动化 ==========
class ContentPlanner:
    """内容排期计划"""
    
    def __init__(self):
        self.calendar = {
            "周一": {"B站": "技术教程", "小红书": "工具推荐", "朋友圈": "案例"},
            "周二": {"B站": "效果展示", "小红书": "体验分享", "朋友圈": "干货"},
            "周三": {"B站": "经验分享", "小红书": "行业分析", "朋友圈": "动态"},
            "周四": {"B站": "工具测评", "小红书": "避坑指南", "朋友圈": "好评"},
            "周五": {"B站": "行业思考", "小红书": "效率工具", "朋友圈": "福利"},
            "周六": {"小红书": "周末分享", "朋友圈": "个人内容"},
            "周日": {"朋友圈": "下周预告"}
        }
    
    def generate_weekly_plan(self):
        """生成周度内容计划"""
        plan = []
        for day, contents in self.calendar.items():
            day_plan = f"{day}："
            for platform, content in contents.items():
                day_plan += f"\n  📱 {platform} → {content}"
            plan.append(day_plan)
        return plan

# ========== 获客漏斗 ==========
class CustomerFunnel:
    """客户转化漏斗"""
    
    def __init__(self):
        self.stages = {
            "曝光": 10000,
            "点击": 500,
            "咨询": 50,
            "报价": 20,
            "成交": 5
        }
    
    def calculate_conversion(self):
        """计算转化率"""
        results = []
        stages_list = list(self.stages.items())
        for i in range(len(stages_list)-1):
            stage_name, stage_count = stages_list[i]
            next_name, next_count = stages_list[i+1]
            rate = (next_count / stage_count) * 100
            results.append(f"{stage_name}({stage_count}) → {next_name}({next_count})：{rate:.1f}%")
        return results
    
    def optimize(self, target_stage, target_value):
        """优化特定阶段的转化"""
        current = self.stages[target_stage]
        improvement = ((target_value - current) / current) * 100
        return f"将{target_stage}从{current}提升到{target_value}，增长{improvement:.1f}%"

if __name__ == "__main__":
    print("=" * 60)
    print("📱 多渠道矩阵获客策略")
    print("=" * 60)
    
    print("\n📺 B站策略")
    print("-" * 40)
    bilibili = ChannelStrategy.bilibili_strategy()
    print(f"特征：{bilibili['平台特征']}")
    print("内容方向：")
    for c in bilibili['内容方向']:
        print(f"  📌 {c['title']}（{c['type']}）")
    print(f"发布频率：{bilibili['发布频率']}")
    print(f"引流：{bilibili['引流方式']}")
    
    print("\n📕 小红书策略")
    print("-" * 40)
    xhs = ChannelStrategy.xiaohongshu_strategy()
    print(f"特征：{xhs['平台特征']}")
    print("内容方向：")
    for c in xhs['内容方向']:
        print(f"  📌 {c['title']}（{c['type']}）")
    print(f"发布频率：{xhs['发布频率']}")
    
    print("\n💬 私域运营")
    print("-" * 40)
    wechat = ChannelStrategy.wechat_private_domain()
    for w in wechat['运营方式']:
        print(f"  • {w}")
    
    print("\n📅 周度内容排期")
    print("-" * 40)
    planner = ContentPlanner()
    for p in planner.generate_weekly_plan():
        print(f"  {p}")
    
    print("\n📊 获客漏斗分析")
    print("-" * 40)
    funnel = CustomerFunnel()
    for r in funnel.calculate_conversion():
        print(f"  {r}")
