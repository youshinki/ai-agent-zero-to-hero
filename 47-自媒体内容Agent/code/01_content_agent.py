# 第47篇配套代码：自媒体内容Agent
# 全自动日更变现赛道
# 运行：python 01_content_agent.py

# ========== 自媒体内容生成Agent ==========
class ContentAgent:
    """全自动自媒体内容创作Agent"""
    
    def __init__(self, platform="小红书", niche="AI工具"):
        self.platform = platform
        self.niche = niche
        self.content_plan = []
    
    def generate_topics(self, count=5):
        """生成选题"""
        topics_pool = {
            "AI工具": [
                "打工人必备的5个AI效率工具",
                "AI写周报居然比我还好？",
                "用AI一天做了10张图",
                "ChatGPT隐藏功能大揭秘",
                "这5个AI神器让我效率翻倍"
            ],
            "职场技能": [
                "新手如何快速提升Python",
                "Excel技巧之VLOOKUP进阶",
                "远程办公效率提升指南",
                "程序员必备的10个工具",
                "产品经理需求文档怎么写"
            ]
        }
        topics = topics_pool.get(self.niche, topics_pool["AI工具"])
        return topics[:count]
    
    def generate_content(self, topic, platform="小红书"):
        """生成内容"""
        if platform == "小红书":
            return self._generate_xiaohongshu(topic)
        elif platform == "公众号":
            return self._generate_wechat(topic)
        else:
            return self._generate_generic(topic)
    
    def _generate_xiaohongshu(self, topic):
        return f"""# {topic}

🔥 标题：{topic}

📌 正文：
你是不是也这样？每天工作忙得要死，效率却很低？
今天分享几个我亲测好用的效率工具，看完绝对有收获！

1️⃣ 工具一：XXX
   - 功能：XXX
   - 亮点：XXX
   - 难度：⭐

2️⃣ 工具二：XXX
   - 功能：XXX
   - 亮点：XXX
   - 难度：⭐⭐

3️⃣ 工具三：XXX
   - 功能：XXX
   - 亮点：XXX
   - 难度：⭐

💡 使用技巧：
- 技巧1：先做XXX再XXX
- 技巧2：搭配XXX使用效果更好

💬 讨论：
你最常用哪个工具？评论区告诉我！

#效率工具 #AI #打工人 #效率提升"""

    def _generate_wechat(self, topic):
        return f"""# {topic}

## 前言
大家好，我是XX。今天和大家聊聊{topic}这个话题。

## 一、为什么要关注这个？
在当前这个快速变化的时代，效率就是竞争力。掌握正确的工具和方法，能让你事半功倍。

## 二、核心方法
### 2.1 方法一
详细说明...

### 2.2 方法二
详细说明...

## 三、实战案例
以我自己的经历为例...

## 四、总结与建议
1. 不要贪多，先掌握2-3个工具
2. 坚持实践，形成习惯
3. 持续学习，保持更新

---
如果觉得有用，欢迎点赞转发！"""
    
    def _generate_generic(self, topic):
        return f"# {topic}\n\n内容生成中..."
    
    def create_posting_schedule(self, days=7):
        """生成发布计划"""
        platforms = {
            "小红书": "每天1-2篇",
            "公众号": "每周2-3篇",
            "B站": "每周1-2个视频",
            "知乎": "每周2-3个回答"
        }
        schedule = []
        for i in range(days):
            from datetime import datetime, timedelta
            date = (datetime.now() + timedelta(days=i)).strftime("%m-%d")
            schedule.append({
                "date": date,
                "platform": list(platforms.keys())[i % len(platforms)],
                "topic": self.generate_topics(1)[0]
            })
        return schedule

# ========== 平台适配 ==========
class PlatformAdapter:
    """各平台内容格式适配"""
    
    @staticmethod
    def format_for_platform(content, platform):
        if platform == "小红书":
            return content[:1000] + "\n\n#效率工具 #AI"
        elif platform == "知乎":
            return content + "\n\n---\n编辑于 " + __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        elif platform == "B站":
            return f"【脚本】\n{content}\n\n【时间轴】\n00:00 - 开场\n01:00 - 正文\n03:00 - 总结"
        return content

if __name__ == "__main__":
    print("=" * 60)
    print("📱 自媒体内容Agent - 全自动日更变现")
    print("=" * 60)
    
    agent = ContentAgent("小红书", "AI工具")
    
    print("\n📌 选题生成")
    print("-" * 40)
    topics = agent.generate_topics(5)
    for t in topics:
        print(f"  • {t}")
    
    print("\n📝 内容生成（小红书风格）")
    print("-" * 40)
    content = agent.generate_content(topics[0], "小红书")
    print(content[:500] + "...")
    
    print("\n📅 7天发布计划")
    print("-" * 40)
    schedule = agent.create_posting_schedule(7)
    for s in schedule:
        print(f"  {s['date']} | {s['platform']} | {s['topic']}")
    
    print("\n💰 变现路径")
    print("-" * 40)
    print("""
  1️⃣ 接单代写：200-500元/篇
  2️⃣ 知识付费：99-299元/课程
  3️⃣ 广告合作：500-5000元/条
  4️⃣ 私域引流：转接单变现（5000+元/单）
  5️⃣ 矩阵运营：多账号多平台，月入2万+
""")
