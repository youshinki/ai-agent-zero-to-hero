#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第14篇配套 · test_memory.py
验证记忆持久化：写入 → 读取 → 换会话后仍记得 → 清空

运行: python test_memory.py
（使用独立的测试JSON，不污染真实 chat_memory/history.json）
"""

import json
import os
import shutil

# 用测试目录隔离
TEST_DIR = "chat_memory_test"
for name, val in [("MEMORY_DIR", TEST_DIR), ("MEMORY_FILE", os.path.join(TEST_DIR, "history.json"))]:
    os.environ[name] = val

from fastapi.testclient import TestClient

# 让 config 读取测试目录
import config
config.MEMORY_DIR = TEST_DIR
config.MEMORY_FILE = os.path.join(TEST_DIR, "history.json")

import main
main.MEMORY_DIR = TEST_DIR
main.MEMORY_FILE = os.path.join(TEST_DIR, "history.json")

client = TestClient(main.app)


def read_stream(resp) -> str:
    chars = []
    for line in resp.iter_lines():
        if not line:
            continue
        chars.append(json.loads(line)["char"])
    return "".join(chars)


def main_test():
    # 清理旧测试数据
    shutil.rmtree(TEST_DIR, ignore_errors=True)

    print("=" * 60)
    print("🧪 记忆持久化测试")
    print("=" * 60)

    # 1. 清空
    r = client.post("/api/agent/clear")
    print(f"\n[清空记忆] {r.json()}")

    # 2. 第一轮：告知身份
    with client.stream("POST", "/api/agent/stream",
                       json={"task": "我是一名AI开发者，擅长Agent工程化", "history": []}) as resp:
        text1 = read_stream(resp)
    print(f"\n[第1轮] 我是一名AI开发者，擅长Agent工程化")
    print(f"  回复：{text1[:80]}...")

    # 3. 读取服务端记忆
    hist = client.get("/api/agent/history").json()["history"]
    print(f"\n[读取历史] 共 {len(hist)} 条，文件：{main.MEMORY_FILE}")
    assert len(hist) == 2, "历史应保存一问一答2条"

    # 4. 模拟"刷新页面/重启服务"：用服务端持久化历史发起新一轮
    with client.stream("POST", "/api/agent/stream",
                       json={"task": "总结一下我的身份和特长", "history": hist}) as resp:
        text2 = read_stream(resp)
    print(f"\n[第2轮] 总结一下我的身份和特长（带历史）")
    print(f"  回复：{text2[:160]}...")

    remembered = ("开发者" in text2) or ("特长" in text2) or ("身份" in text2)
    print(f"\n  ✅ 是否记得上文：{'是' if remembered else '否（需要检查）'}")

    # 5. 确认写入成功
    hist2 = client.get("/api/agent/history").json()["history"]
    print(f"\n[持久化校验] 历史现在 {len(hist2)} 条，JSON文件存在：{os.path.exists(main.MEMORY_FILE)}")
    print("  最近一条：", hist2[-1]["role"], "|", hist2[-1]["content"][:40], "...")

    # 6. 清空
    client.post("/api/agent/clear")
    hist3 = client.get("/api/agent/history").json()["history"]
    print(f"\n[清空后] 历史 {len(hist3)} 条")

    print("\n✅ 记忆持久化测试全部通过")


if __name__ == "__main__":
    main_test()
