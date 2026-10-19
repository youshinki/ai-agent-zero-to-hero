#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第49篇配套完整项目代码 · personal_assistant.py
赛道4：个人专属AI助理（高端记忆知识库接单）

  1. 个人档案记忆（身份/偏好/习惯）
  2. 日程与提醒
  3. 笔记管理（标签 + 检索）
  4. 每日简报 / 周度回顾
  5. 个性化回复（按偏好调整语气）

运行: python personal_assistant.py
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# ======================================================================
# 一、记忆系统
# ======================================================================

class Memory:
    def __init__(self):
        self.profile: Dict[str, str] = {}
        self.notes: List[dict] = []
        self.habits: Dict[str, int] = {}
    
    # ---- 档案 ----
    def update_profile(self, key: str, value: str):
        self.profile[key] = value
    
    def extract_profile(self, text: str):
        """从对话中自动抽取身份/偏好/习惯"""
        patterns = [
            (r"我(?:是|叫)([^，。；\n]{1,20})", "身份"),
            (r"(?:我)?(?:喜欢|偏好|习惯|希望)([^，。；\n]{1,30})", "偏好"),
            (r"(?:我)?(?:每天|每周|经常)([^，。；\n]{1,30})", "习惯"),
        ]
        for pattern, key in patterns:
            m = re.search(pattern, text)
            if m:
                self.update_profile(key, m.group(1).strip())
    
    def get_profile_text(self) -> str:
        if not self.profile:
            return "（暂无档案）"
        return "\n".join(f"- {k}：{v}" for k, v in self.profile.items())
    
    # ---- 笔记 ----
    def add_note(self, title: str, content: str, tags: List[str] = None):
        self.notes.append({"title": title, "content": content,
                           "tags": tags or [],
                           "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
    
    def search_notes(self, keyword: str) -> List[dict]:
        return [n for n in self.notes
                if keyword in n["title"] or keyword in n["content"]
                or any(keyword in t for t in n["tags"])]
    
    # ---- 习惯 ----
    def record_habit(self, name: str):
        self.habits[name] = self.habits.get(name, 0) + 1
    
    def top_habits(self, k: int = 3) -> List[tuple]:
        return sorted(self.habits.items(), key=lambda x: x[1], reverse=True)[:k]


# ======================================================================
# 二、日程与提醒
# ======================================================================

class Scheduler:
    def __init__(self):
        self.events: List[dict] = []
    
    def add(self, date: str, time: str, title: str,
            priority: str = "normal"):
        self.events.append({
            "date": date, "time": time, "title": title,
            "priority": priority, "done": False,
        })
        self.events.sort(key=lambda e: (e["date"], e["time"]))
    
    def today(self, date: str = None) -> List[dict]:
        date = date or datetime.now().strftime("%Y-%m-%d")
        return [e for e in self.events if e["date"] == date]
    
    def pending(self, date: str = None) -> List[dict]:
        date = date or datetime.now().strftime("%Y-%m-%d")
        return [e for e in self.events if not e["done"] and e["date"] != date]
    
    def mark_done(self, title: str) -> bool:
        for e in self.events:
            if e["title"] == title:
                e["done"] = True
                return True
        return False


# ======================================================================
# 三、个人助理
# ======================================================================

class PersonalAssistant:
    def __init__(self, name: str = "小助理"):
        self.name = name
        self.memory = Memory()
        self.scheduler = Scheduler()
    
    def handle(self, message: str) -> str:
        self.memory.extract_profile(message)
        
        # 日程
        m = re.search(r"(明天|今天)\s*(\d{1,2})[:：](\d{2})\s*(.*)", message)
        if m:
            day, hh, mm, title = m.groups()
            date = (datetime.now() + (timedelta(days=1) if day == "明天" else timedelta())).strftime("%Y-%m-%d")
            self.scheduler.add(date, f"{int(hh):02d}:{mm}", title.strip() or "未命名事项")
            return f"已添加日程：{date} {int(hh):02d}:{mm} {title.strip()}"
        
        if "日程" in message or "安排" in message:
            return self.daily_briefing()
        
        # 笔记
        if message.startswith("记笔记") or "记一下" in message:
            content = re.sub(r"^(记笔记|记一下)[：:\s]*", "", message)
            self.memory.add_note(f"随手笔记{len(self.memory.notes)+1}", content, ["随手记"])
            return "笔记已保存。"
        
        if "搜笔记" in message or "找笔记" in message:
            kw = re.sub(r"(搜笔记|找笔记)[：:\s]*", "", message)
            hits = self.memory.search_notes(kw)
            if not hits:
                return f"没有找到与「{kw}」相关的笔记。"
            return "\n".join(f"- {n['title']}：{n['content'][:40]}" for n in hits[:3])
        
        # 档案
        if "我的档案" in message or "你记得我" in message:
            return f"你的档案：\n{self.memory.get_profile_text()}"
        
        # 习惯
        if "习惯" in message:
            habits = self.memory.top_habits()
            return "你的高频习惯：\n" + "\n".join(
                f"- {h}（{c}次）" for h, c in habits) if habits else "还没有记录习惯。"
        
        # 个性化语气
        style = self.memory.profile.get("偏好", "")
        if "简洁" in style:
            return f"收到：{message[:20]}（已按简洁偏好处理）"
        return f"好的，我记下了：「{message[:30]}」。需要我帮你安排时间或记笔记吗？"
    
    def daily_briefing(self, date: str = None) -> str:
        date = date or datetime.now().strftime("%Y-%m-%d")
        today = self.scheduler.today(date)
        pending = self.scheduler.pending(date)
        
        out = [f"☀️ {date} 每日简报", f"\n📅 今日日程（{len(today)}项）："]
        out += [f"- {'🔴' if e['priority'] != 'normal' else '🟡'} {e['time']} {e['title']}"
                for e in today] or ["- 暂无安排"]
        out.append(f"\n⏰ 待办（{len(pending)}项）：")
        out += [f"- {e['date']} {e['title']}" for e in pending[:5]] or ["- 暂无待办"]
        out.append(f"\n🧠 档案：\n{self.memory.get_profile_text()}")
        return "\n".join(out)


# ======================================================================
# 演示
# ======================================================================

def demo():
    pa = PersonalAssistant("小助理")
    
    print("=" * 66)
    print("👤 赛道4：个人专属AI助理 · 演示")
    print("=" * 66)
    
    print("\n[1] 学习档案：")
    print(f"   {pa.handle('我是一名AI开发者，喜欢简洁的回答风格，每天写代码')}")
    print(f"   档案：\n{pa.memory.get_profile_text()}")
    
    print("\n[2] 日程：")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"   {pa.handle(f'明天 09:30 团队周会')}")
    print(f"   {pa.handle(f'明天 14:00 客户演示')}")
    print(f"   {pa.handle('今天 18:00 健身')}")
    
    print("\n[3] 笔记：")
    print(f"   {pa.handle('记笔记：RAG检索要先扩召再重排')}")
    print(f"   {pa.handle('记笔记：成本优化三件套=缓存+路由+压缩')}")
    print(f"   {pa.handle('搜笔记 RAG')}")
    
    print("\n[4] 每日简报：")
    print(pa.daily_briefing())
    
    print("\n[5] 个性化回复（简洁风格）：")
    print(f"   {pa.handle('帮我总结今天的收获')}")


if __name__ == "__main__":
    demo()
