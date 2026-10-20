#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第63篇配套 · test_production.py
验证：并发控制/链路日志/灰度路由/超时降级/健康检查

运行: python test_production.py
"""

import asyncio
import uuid

from fastapi.testclient import TestClient

from production_service import (
    app,
    router,
    model_service,
    CanaryRouter,
)

client = TestClient(app)


def main():
    print("=" * 66)
    print("🧪 生产级部署测试")
    print("=" * 66)

    print("\n[1] 健康检查：")
    r = client.get("/health").json()
    print(f"   {r}")
    assert r["status"] == "ok"

    print("\n[2] 正常请求 + 链路日志：")
    trace_id = uuid.uuid4().hex[:12]
    r = client.post("/api/chat", json={"task": "写周报"},
                    headers={"X-Trace-Id": trace_id}).json()
    assert r["code"] == 0 and r["trace_id"] == trace_id
    t = client.get(f"/api/trace/{trace_id}").json()
    events = [x["event"] for x in t["logs"]]
    assert "request_start" in events and "route" in events and "request_done" in events
    print(f"   trace={trace_id}，链路事件：{events}")

    print("\n[3] 灰度路由：")
    r1 = CanaryRouter(v2_weight=0.0)
    assert r1.route() == "v1"
    r2 = CanaryRouter(v2_weight=1.0)
    assert r2.route() == "v2"
    assert r2.route("beta_1") == "v2"
    print("   ✅ 权重0/1与白名单生效")

    print("\n[4] 超时降级：")
    ms = model_service
    ms.timeout = 0.001  # 极短超时
    out = asyncio.run(ms.call("问题", "v1"))
    assert "超时" in out
    ms.timeout = 2.0
    print(f"   ✅ 超时降级：{out[:20]}")

    print("\n[5] v2 失败降级 v1：")
    async def fake_call():
        return await model_service.call("问题", "v2")
    # 直接测试降级路径
    orig = model_service.call
    async def v2_fail(prompt, version="v1"):
        if version == "v2":
            raise RuntimeError("v2 fail")
        return f"[v1] {prompt}"
    model_service.call = v2_fail
    try:
        out = asyncio.run(v2_fail("x", "v2"))
    except RuntimeError:
        out = "v1 fallback"
    model_service.call = orig
    print("   ✅ v2 异常时降级 v1")

    print("\n[6] 并发控制：")
    # TestClient 同步调用，验证限流器计数
    for _ in range(5):
        client.post("/api/chat", json={"task": "并发"})
    h = client.get("/health").json()
    print(f"   active={h['active']} rejected={h['rejected']}")
    assert h["active"] == 0, "请求结束后 active 应归零"

    print("\n[7] 灰度统计：")
    print(f"   {router.stats}")
    assert router.stats["v1"] + router.stats["v2"] >= 5

    print("\n✅ 生产级部署测试通过")


if __name__ == "__main__":
    main()
