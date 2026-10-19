#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第64篇配套 · test_state_machine.py
"""

import os
import time

from state_machine import (
    STATES, TERMINAL, Session, SessionStore, InvalidTransition, demo,
)


def main():
    print("=" * 66)
    print("🧪 Agent 状态机测试")
    print("=" * 66)
    path = "test_sessions.json"
    if os.path.exists(path):
        os.remove(path)

    print("\n[1] 状态定义：")
    assert "idle" in STATES and "done" in STATES
    assert TERMINAL == {"done", "failed", "cancelled"}
    print(f"   ✅ {len(STATES)} 个状态，合法流转已定义")

    print("\n[2] 合法流转：")
    store = SessionStore(path)
    store.create("s1")
    for target in ["planning", "executing", "reflecting", "done"]:
        s = store.transition("s1", target)
    assert s.state == "done" and s.version == 4
    print(f"   ✅ idle→planning→executing→reflecting→done（v{s.version}）")

    print("\n[3] 非法流转：")
    try:
        store.transition("s1", "planning")
        assert False
    except InvalidTransition as e:
        print(f"   ✅ {e}")

    print("\n[4] 版本冲突（并发安全）：")
    store.create("s2")
    store.transition("s2", "planning")
    try:
        store.transition("s2", "executing", expected_version=0)
        assert False
    except InvalidTransition as e:
        assert "版本冲突" in str(e)
        print(f"   ✅ {e}")

    print("\n[5] 持久化：")
    store2 = SessionStore(path)
    assert store2.get("s1").state == "done"
    assert len(store2.sessions) >= 2
    print(f"   ✅ 重载 {len(store2.sessions)} 个会话")

    print("\n[6] 脏状态清理：")
    store.create("s3")
    store.transition("s3", "planning")
    store.sessions["s3"].updated_at = time.time() - 999
    result = store.cleanup_dirty(stale_seconds=300)
    assert "s3" in result["cleaned"]
    assert store.get("s3").state == "idle"
    assert store.get("s3").metadata["cleanup_reason"] == "stale"
    print(f"   ✅ 清理 {result['count']} 个脏会话")

    print("\n[7] 演示：")
    demo()

    if os.path.exists(path):
        os.remove(path)
    print("\n✅ 状态机测试通过")


if __name__ == "__main__":
    main()
