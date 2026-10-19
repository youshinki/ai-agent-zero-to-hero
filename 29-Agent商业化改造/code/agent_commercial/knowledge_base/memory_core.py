#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第28篇配套完整项目代码 · knowledge_base/memory_core.py
长期记忆核心引擎（静态知识库之外的动态记忆库）

  - 对话永久存储（自动去重）
  - 用户偏好档案
  - 近期记忆检索
  - 记忆条数上限，防止无限膨胀
==========================================================================
"""

import json
import os
import time
from typing import Dict


# 长期记忆存储路径
MEMORY_STORE_PATH = "knowledge_base/memory_store.json"
MAX_CHAT_MEMORY = 100
KEEP_RECENT = 80


class LongTermMemory:
    def __init__(self, store_path: str = MEMORY_STORE_PATH):
        self.store_path = store_path
        self.store = self.load_memory()
    
    # ---------------- 读写 ----------------
    def load_memory(self) -> Dict:
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data.setdefault("user_profile", {})
                data.setdefault("chat_memory", [])
                data.setdefault("update_time", time.strftime("%Y-%m-%d %H:%M:%S"))
                return data
            except (json.JSONDecodeError, OSError):
                pass
        return {
            "user_profile": {},
            "chat_memory": [],
            "update_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def save_memory(self):
        os.makedirs(os.path.dirname(self.store_path) or ".", exist_ok=True)
        self.store["update_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self.store, f, ensure_ascii=False, indent=2)
    
    # ---------------- 对话记忆 ----------------
    def add_chat_memory(self, user_query: str, bot_answer: str):
        """新增对话记忆（自动去重：同问题覆盖答案）"""
        for item in self.store["chat_memory"]:
            if item["query"] == user_query:
                item["answer"] = bot_answer
                item["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.save_memory()
                return
        
        self.store["chat_memory"].append({
            "query": user_query,
            "answer": bot_answer,
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        
        # 限制最大条数
        if len(self.store["chat_memory"]) > MAX_CHAT_MEMORY:
            self.store["chat_memory"] = self.store["chat_memory"][-KEEP_RECENT:]
        
        self.save_memory()
    
    # ---------------- 用户档案 ----------------
    def update_user_profile(self, key: str, value: str):
        self.store["user_profile"][key] = value
        self.save_memory()
    
    def get_user_profile(self) -> str:
        if not self.store["user_profile"]:
            return ""
        text = "【用户个人偏好档案】\n"
        for k, v in self.store["user_profile"].items():
            text += f"- {k}：{v}\n"
        return text
    
    # ---------------- 检索记忆 ----------------
    def get_recent_memory(self, top_k: int = 5) -> str:
        recent = self.store["chat_memory"][-top_k:]
        if not recent:
            return "【用户长期对话记忆】\n（暂无历史对话）\n"
        text = "【用户长期对话记忆】\n"
        for idx, item in enumerate(recent, 1):
            text += f"{idx}. 用户：{item['query']}\n   助手：{item['answer'][:120]}\n"
        return text
    
    def search_memory(self, query: str, top_k: int = 3) -> str:
        """按关键词相似度检索历史记忆（轻量本地实现）"""
        memories = self.store["chat_memory"]
        if not memories:
            return ""
        
        def overlap(a: str, b: str) -> int:
            sa, sb = set(a), set(b)
            return len(sa & sb)
        
        scored = [(overlap(query, m["query"] + m["answer"]), m) for m in memories]
        scored.sort(key=lambda x: x[0], reverse=True)
        top = [m for s, m in scored[:top_k] if s > 0]
        if not top:
            return ""
        
        text = "【相关历史记忆】\n"
        for i, m in enumerate(top, 1):
            text += f"{i}. 用户曾问：{m['query']}\n   当时回答：{m['answer'][:100]}\n"
        return text
    
    # ---------------- 管理 ----------------
    def clear_memory(self) -> str:
        self.store = {
            "user_profile": {},
            "chat_memory": [],
            "update_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.save_memory()
        return "长期记忆已全部清空"
    
    def stats(self) -> dict:
        return {
            "profile_items": len(self.store["user_profile"]),
            "chat_memories": len(self.store["chat_memory"]),
            "update_time": self.store.get("update_time", ""),
            "store_path": self.store_path,
        }


memory = LongTermMemory()
