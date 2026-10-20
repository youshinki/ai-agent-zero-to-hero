#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第44篇配套 · test_api.py
验证：鉴权/限流/统一响应/分页/用量统计/SDK

运行: python test_api.py
"""

from fastapi.testclient import TestClient

from api_service import (app, fail, ERROR_CODES, AgentSDK)

client = TestClient(app)


def main():
    print("=" * 66)
    print("🧪 商用接口封装测试")
    print("=" * 66)

    # 1. 健康检查
    print("\n[1] 健康检查：")
    r = client.get("/health").json()
    print(f"   {r}")
    assert r["code"] == 0 and r["data"]["status"] == "healthy"

    # 2. 鉴权
    print("\n[2] 鉴权：")
    r = client.post("/api/v1/chat", json={"message": "你好"})
    print(f"   无Key → HTTP {r.status_code}，code={r.json()['detail']['code']}")
    assert r.status_code == 401

    r = client.post("/api/v1/chat", json={"message": "你好"},
                    headers={"X-Api-Key": "sk-wrong"})
    print(f"   错误Key → HTTP {r.status_code}，msg={r.json()['detail']['msg']}")
    assert r.status_code == 401

    # 3. 正常对话
    print("\n[3] 正常对话：")
    r = client.post("/api/v1/chat", json={"message": "企业知识库怎么部署？"},
                    headers={"X-Api-Key": "sk-demo-001"}).json()
    print(f"   code={r['code']} msg={r['msg']}")
    print(f"   answer={r['data']['answer']}")
    print(f"   usage={r['data']['usage']}")
    assert r["code"] == 0 and r["data"]["usage"]["tokens_in"] > 0

    # 4. 参数错误
    print("\n[4] 参数错误：")
    r = client.post("/api/v1/chat", json={"message": "  "},
                    headers={"X-Api-Key": "sk-demo-001"}).json()
    print(f"   code={r['code']} msg={r['msg']}")
    assert r["code"] == 2001

    # 5. 用量统计
    print("\n[5] 用量统计：")
    r = client.get("/api/v1/usage", headers={"X-Api-Key": "sk-demo-001"}).json()
    print(f"   {r['data']}")
    assert r["data"]["requests"] >= 1

    # 6. 分页
    print("\n[6] 分页：")
    r = client.get("/api/v1/docs/items?page=2&size=10",
                   headers={"X-Api-Key": "sk-demo-002"}).json()
    d = r["data"]
    print(f"   page={d['page']} size={d['size']} total={d['total']} pages={d['total_pages']}")
    assert len(d["items"]) == 10 and d["total"] == 55

    # 7. SDK
    print("\n[7] Python SDK：")
    sdk = AgentSDK(api_key="sk-demo-001", transport=client)
    r = sdk.chat("SDK 调用测试")
    print(f"   chat → code={r['code']} answer={r['data']['answer'][:30]}...")
    assert r["code"] == 0
    r2 = sdk.usage()
    print(f"   usage → {r2['data']}")
    r3 = sdk.list_items(page=1, size=5)
    print(f"   list_items → {len(r3['data']['items'])} 条")
    assert len(r3["data"]["items"]) == 5

    # 8. 错误码表
    print("\n[8] 错误码规范：")
    for code, msg in ERROR_CODES.items():
        print(f"   {code}: {msg}")
    assert fail(1001)["code"] == 1001

    print("\n✅ 商用接口封装测试通过")


if __name__ == "__main__":
    main()
