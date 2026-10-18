# 第49篇配套代码：个人专属AI助理
# 高端记忆知识库接单赛道
# 运行：python 01_personal_assistant.py

# ========== 个人专属AI助理 ==========
class PersonalAssistant:
    """个人专属AI助理"""
    
    def __init__(self, owner_name):
        self.owner = owner_name
        self.preferences = {}
        self.schedule = []
        self.notes = []
        self.habits = {}
    
    def learn_preference(self, category, value):
        """学习用户偏好"""
        self.preferences[category] = value
        return f"已记住：{category} → {value}"
    
    def add_schedule(self, time, event, priority="normal"):
        """添加日程"""
        self.schedule.append({
            "time": time,
            "event": event,
            "priority": priority,
            "done": False
        })
        self.schedule.sort(key=lambda x: x["time"])
        return f"✅ 已添加日程：{time} {event}"
    
    def add_note(self, title, content, tags=None):
        """添加笔记"""
        note = {
            "title": title,
            "content": content,
            "tags": tags or [],
            "created": "now"
        }
        self.notes.append(note)
        return f"📝 笔记「{title}」已保存"
    
    def daily_briefing(self):
        """生成每日简报"""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 今日日程
        today_schedule = [s for s in self.schedule if today in s["time"]]
        
        briefing = f"☀️ {self.owner}，早上好！这是今天的简报：\n\n"
        briefing += f"📅 今日日程（{len(today_schedule)}项）：\n"
        if today_schedule:
            for s in today_schedule:
                briefing += f"  {'🔴' if s['priority']=='high' else '🟡'} {s['time']} {s['event']}\n"
        else:
            briefing += "  暂无安排\n"
        
        # 待办提醒
        pending = [s for s in self.schedule if not s["done"] and today not in s["time"]]
        if pending:
            briefing += f"\n⏰ 待办事项（{len(pending)}项）：\n"
            for p in pending[:3]:
                briefing += f"  • {p['event']}\n"
        
        return briefing
    
    def search_notes(self, keyword):
        """搜索笔记"""
        results = []
        for note in self.notes:
            if keyword in note["title"] or keyword in note["content"]:
                results.append(note)
        return results
    
    def get_personalized_response(self, user_input):
        """根据个人偏好生成个性化回复"""
        style = self.preferences.get("回复风格", "正式")
        if style == "轻松":
            return f"嘿！关于「{user_input}」，我的想法是这样的..."
        elif style == "简洁":
            return f"关于{user_input}：核心要点如下..."
        else:
            return f"您好，关于「{user_input}」的回复如下：详细内容..."

# ========== 记忆系统 ==========
class MemorySystem:
    """个人记忆系统"""
    
    def __init__(self):
        self.memories = {}
    
    def remember(self, key, value, category="general"):
        """记住信息"""
        self.memories[key] = {
            "value": value,
            "category": category,
            "time": "now"
        }
    
    def recall(self, key):
        """回忆信息"""
        return self.memories.get(key, {}).get("value", "我不记得了")
    
    def get_memories_by_category(self, category):
        return {k: v for k, v in self.memories.items() if v["category"] == category}

if __name__ == "__main__":
    print("=" * 60)
    print("👤 个人专属AI助理")
    print("=" * 60)
    
    assistant = PersonalAssistant("小明")
    
    print("\n1️⃣ 学习偏好")
    print("-" * 40)
    print(assistant.learn_preference("回复风格", "轻松"))
    print(assistant.learn_preference("工作时间", "9:00-18:00"))
    print(assistant.learn_preference("兴趣", "AI技术、编程"))
    
    print("\n2️⃣ 日程管理")
    print("-" * 40)
    print(assistant.add_schedule("2024-01-15 09:00", "团队周会", "high"))
    print(assistant.add_schedule("2024-01-15 14:00", "客户演示", "high"))
    print(assistant.add_schedule("2024-01-16 10:00", "代码评审"))
    
    print("\n3️⃣ 笔记管理")
    print("-" * 40)
    print(assistant.add_note("Python装饰器笔记", "装饰器是一种设计模式...", ["Python", "编程"]))
    print(assistant.add_note("项目架构设计", "采用微服务架构...", ["架构", "项目"]))
    
    print("\n4️⃣ 每日简报")
    print("-" * 40)
    print(assistant.daily_briefing())
    
    print("\n5️⃣ 个性化回复")
    print("-" * 40)
    print(assistant.get_personalized_response("今天有什么安排"))
    
    print("\n6️⃣ 记忆系统")
    print("-" * 40)
    memory = MemorySystem()
    memory.remember("最喜欢的书", "《AI未来》", "兴趣")
    memory.remember("生日", "1995-06-15", "个人信息")
    print(f"  最喜欢的书：{memory.recall('最喜欢的书')}")
    print(f"  兴趣分类记忆：{memory.get_memories_by_category('兴趣')}")
