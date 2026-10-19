#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第12篇配套 · test_client.py
无需启动服务器，直接用 FastAPI TestClient 验证接口（CI/无端口环境友好）

运行: python test_client.py
"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def main():
    print("=" * 60)
    print("🧪 API 服务接口测试")
    print("=" * 60)

    # 1. 健康检测
    r = client.get("/health")
    print(f"\n[GET /health] {r.status_code} {r.json()}")

    # 2. 根路径
    r = client.get("/")
    print(f"\n[GET /] {r.status_code} {r.json()}")

    # 3. 核心接口
    payload = {"task": "帮我梳理一下AI Agent的核心开发流程"}
    r = client.post("/api/agent/run", json=payload)
    print(f"\n[POST /api/agent/run] {r.status_code}")
    data = r.json()
    print(f"  code: {data['code']}  msg: {data['msg']}")
    if data.get("data"):
        d = data["data"]
        print(f"  用户任务: {d['user_task']}")
        print(f"  规划长度: {len(d['task_plan'])}字")
        print(f"  原始输出: {len(d['raw_result'])}字")
        print(f"  最终结果: {len(d['final_result'])}字")

    # 4. 异常入参
    r = client.post("/api/agent/run", json={})
    print(f"\n[异常入参] {r.status_code}（422=参数校验生效）")

    print("\n✅ 接口测试完成")


if __name__ == "__main__":
    main()
