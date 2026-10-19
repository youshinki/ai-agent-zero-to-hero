#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第13篇配套 · test_stream.py
不启动服务器，用 TestClient 验证流式接口逐字推送

运行: python test_stream.py
"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def main():
    print("=" * 60)
    print("🧪 流式接口测试（逐字推送）")
    print("=" * 60)

    # 健康检测
    r = client.get("/health")
    print(f"\n[GET /health] {r.status_code} {r.json()}")

    # 流式接口
    payload = {"task": "帮我规划高效的每日学习流程"}
    with client.stream("POST", "/api/agent/stream", json=payload) as resp:
        print(f"\n[POST /api/agent/stream] {resp.status_code} media_type={resp.headers.get('content-type')}")
        chars = []
        for line in resp.iter_lines():
            if not line:
                continue
            import json
            data = json.loads(line)
            chars.append(data["char"])
        text = "".join(chars)
        print(f"  收到 {len(chars)} 个字符块，拼成 {len(text)} 字")
        print("  前80字：", text[:80].replace("\n", " ") + "...")

    print("\n✅ 流式测试完成（每个字符是一个独立事件帧）")


if __name__ == "__main__":
    main()
