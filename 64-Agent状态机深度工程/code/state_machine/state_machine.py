#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第64篇配套完整项目代码 · state_machine.py
Agent 状态机深度工程：会话持久化、状态流转与脏状态清理

  1. 会话状态定义与合法流转
  2. 持久化（JSON 存储）
  3. 脏状态检测与清理
  4. 超时会话回收
  5. 幂等与并发安全（版本号）
==========================================================================
"""

import json
import os
import time
from typing import Dict, List, Optional


# ======================================================================
# 一、状态定义
# ======================================================================

STATES = {
    "idle": ["planning", "cancelled"],
    "planning": ["executing", "failed", "cancelled"],
    "executing": ["reflecting", "failed", "cancelled"],
    "reflecting": ["done", "executing", "failed"],
    "done": ["idle"],
    "failed": ["idle", "planning"],
    "cancelled": ["idle"],
}

TERMINAL = {"done", "failed", "cancelled"}


class InvalidTransition(Exception):
    pass


# ======================================================================
# 二、会话状态机
# ======================================================================

class Session:
    def __init__(self, session_id: str, state: str = "idle",
                 version: int = 0):
        self.session_id = session_id
        self.state = state
        self.version = version
        self.updated_at = time.time()
        self.metadata: Dict = {}
    
    def can_transition(self, target: str) -> bool:
        return target in STATES.get(self.state, [])
    
    def transition(self, target: str, expected_version: Optional[int] = None):
        if expected_version is not None and expected_version != self.version:
            raise InvalidTransition(
                f"版本冲突：期望{expected_version}，实际{self.version}")
        if not self.can_transition(target):
            raise InvalidTransition(f"非法流转：{self.state} → {target}")
        self.state = target
        self.version += 1
        self.updated_at = time.time()
        return self
    
    def to_dict(self) -> Dict:
        return {"session_id": self.session_id, "state": self.state,
                "version": self.version, "updated_at": self.updated_at,
                "metadata": self.metadata}
    
    @classmethod
    def from_dict(cls, d: Dict) -> "Session":
        s = cls(d["session_id"], d["state"], d.get("version", 0))
        s.updated_at = d.get("updated_at", time.time())
        s.metadata = d.get("metadata", {})
        return s


# ======================================================================
# 三、持久化存储
# ======================================================================

class SessionStore:
    def __init__(self, path: str = "sessions.json"):
        self.path = path
        self.sessions: Dict[str, Session] = {}
        self.load()
    
    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.sessions = {k: Session.from_dict(v)
                                 for k, v in data.items()}
            except (json.JSONDecodeError, OSError):
                self.sessions = {}
    
    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({k: v.to_dict() for k, v in self.sessions.items()},
                      f, ensure_ascii=False, indent=2)
    
    def create(self, session_id: str) -> Session:
        s = Session(session_id)
        self.sessions[session_id] = s
        self.save()
        return s
    
    def get(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)
    
    def transition(self, session_id: str, target: str,
                   expected_version: int = None) -> Session:
        s = self.get(session_id)
        if not s:
            raise InvalidTransition(f"会话不存在：{session_id}")
        s.transition(target, expected_version)
        self.save()
        return s
    
    # ---------------- 脏状态清理 ----------------
    def dirty_sessions(self, stale_seconds: float = 300) -> List[str]:
        """处于非终态且长时间未更新 → 脏状态"""
        now = time.time()
        return [sid for sid, s in self.sessions.items()
                if s.state not in TERMINAL
                and now - s.updated_at > stale_seconds]
    
    def cleanup_dirty(self, stale_seconds: float = 300) -> Dict:
        dirty = self.dirty_sessions(stale_seconds)
        for sid in dirty:
            s = self.sessions[sid]
            # 强制回到 idle，记录原因
            s.state = "idle"
            s.version += 1
            s.updated_at = time.time()
            s.metadata["cleanup_reason"] = "stale"
        self.save()
        return {"cleaned": dirty, "count": len(dirty)}


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("🧩 Agent 状态机演示")
    print("=" * 66)
    
    store = SessionStore("demo_sessions.json")
    s = store.create("s1")
    print(f"\n[1] 创建会话：{s.state}")
    
    print("\n[2] 正常流转：")
    for target in ["planning", "executing", "reflecting", "done"]:
        s = store.transition("s1", target)
        print(f"   → {s.state}（v{s.version}）")
    
    print("\n[3] 非法流转：")
    try:
        store.transition("s1", "executing")
    except InvalidTransition as e:
        print(f"   ❌ {e}")
    
    print("\n[4] 版本冲突：")
    s2 = store.create("s2")
    store.transition("s2", "planning")
    try:
        store.transition("s2", "executing", expected_version=0)
    except InvalidTransition as e:
        print(f"   ❌ {e}")
    
    print("\n[5] 脏状态清理：")
    s3 = store.create("s3")
    store.transition("s3", "planning")
    s3.updated_at = time.time() - 999  # 模拟长时间未更新
    result = store.cleanup_dirty(stale_seconds=300)
    print(f"   清理：{result}")
    
    print("\n[6] 持久化重载：")
    store2 = SessionStore("demo_sessions.json")
    print(f"   重载会话数：{len(store2.sessions)}")
    print(f"   s1状态：{store2.get('s1').state}")
    
    os.remove("demo_sessions.json")


if __name__ == "__main__":
    demo()
