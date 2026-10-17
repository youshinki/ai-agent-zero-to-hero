import json
import os
import time
from typing import List, Dict

# 长期记忆存储路径
MEMORY_STORE_PATH = "knowledge_base/memory_store.json"

class LongTermMemory:
    def __init__(self):
        self.store = self.load_memory()

    def load_memory(self) -> Dict:
        """加载本地长期记忆"""
        if os.path.exists(MEMORY_STORE_PATH):
            with open(MEMORY_STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        # 初始化记忆结构
        return {
            "user_profile": {},
            "chat_memory": [],
            "update_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def save_memory(self):
        """保存记忆到本地文件"""
        self.store["update_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(MEMORY_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.store, f, ensure_ascii=False, indent=2)

    def add_chat_memory(self, user_query: str, bot_answer: str):
        """新增对话记忆，自动去重"""
        # 去重：重复对话不重复存储
        for item in self.store["chat_memory"]:
            if item["query"] == user_query:
                item["answer"] = bot_answer
                item["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.save_memory()
                return

        # 新增记忆条目
        self.store["chat_memory"].append({
            "query": user_query,
            "answer": bot_answer,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        })

        # 限制记忆最大条数，防止无限膨胀
        if len(self.store["chat_memory"]) > 100:
            self.store["chat_memory"] = self.store["chat_memory"][-80:]
        
        self.save_memory()

    def update_user_profile(self, key: str, value: str):
        """更新用户个人偏好档案"""
        self.store["user_profile"][key] = value
        self.save_memory()

    def get_recent_memory(self, top_k: int = 5) -> str:
        """获取最近对话记忆"""
        recent = self.store["chat_memory"][-top_k:]
        memory_text = "【用户长期对话记忆】\n"
        for idx, item in enumerate(recent, 1):
            memory_text += f"{idx}. 用户：{item['query']}\n   助手：{item['answer']}\n"
        return memory_text

    def get_user_profile(self) -> str:
        """获取用户个人偏好"""
        if not self.store["user_profile"]:
            return ""
        profile_text = "【用户个人偏好档案】\n"
        for k, v in self.store["user_profile"].items():
            profile_text += f"- {k}：{v}\n"
        return profile_text

    def clear_memory(self):
        """清空所有记忆"""
        self.store = {
            "user_profile": {},
            "chat_memory": [],
            "update_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_memory()
        return "长期记忆已全部清空"

# 全局单例
memory = LongTermMemory()
