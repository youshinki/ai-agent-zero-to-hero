#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第62篇配套 · test_streaming.py
验证：SSE 事件流 / WebSocket / 中断 / 局部渲染

运行: python test_streaming.py
"""

import json

from fastapi.testclient import TestClient

from streaming_service import app, PartialRenderer

client = TestClient(app)


def parse_sse(text: str):
    events = []
    for block in text.strip().split("\n\n"):
        if not block.strip():
            continue
        ev = {"event": None, "data": None}
        for line in block.splitlines():
            if line.startswith("event:"):
                ev["event"] = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                ev["data"] = json.loads(line.split(":", 1)[1].strip())
        events.append(ev)
    return events


def main():
    print("=" * 66)
    print("🧪 流式输出工程测试")
    print("=" * 66)

    print("\n[1] 健康检查：")
    r = client.get("/health").json()
    print(f"   {r}")
    assert r["status"] == "ok"

    print("\n[2] SSE 流：")
    r = client.post("/api/stream/sse", json={"task": "写周报", "chunk_size": 6})
    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]
    events = parse_sse(r.text)
    chunks = [e["data"]["chunk"] for e in events if e["event"] == "chunk"]
    done = [e for e in events if e["event"] == "done"]
    assert chunks and done, "应有chunk与done事件"
    full = "".join(chunks)
    assert "写周报" in full
    print(f"   {len(chunks)}个chunk，拼接{len(full)}字")
    print(f"   前20字：{full[:20]}")
    assert done[0]["data"]["total"] == len(full)

    print("\n[3] 中断控制：")
    import asyncio
    from streaming_service import sse_generator
    cancel = {"cancelled": True}
    async def collect():
        out = []
        async for x in sse_generator("测试中断", 4, cancel):
            out.append(x)
        return out
    events2 = asyncio.run(collect())
    assert any("cancelled" in e for e in events2)
    assert not any("event: done" in e for e in events2)
    print("   ✅ 中断事件生效，未输出done")

    print("\n[4] WebSocket：")
    with client.websocket_connect("/ws/stream") as ws:
        ws.send_json({"action": "ask", "task": "写周报"})
        msgs = []
        while True:
            m = ws.receive_json()
            msgs.append(m)
            if m["event"] in ("done", "cancelled"):
                break
        chunks_ws = [m["chunk"] for m in msgs if m["event"] == "chunk"]
        assert chunks_ws and msgs[-1]["event"] == "done"
        print(f"   {len(chunks_ws)}个chunk + done")

    # 中断
    with client.websocket_connect("/ws/stream") as ws:
        ws.send_json({"action": "cancel"})
        m = ws.receive_json()
        assert m["event"] == "cancelled"
        print("   ✅ WebSocket 中断")

    print("\n[5] 局部渲染：")
    pr = PartialRenderer()
    for c in ["这是", "一段", "流式", "文本"]:
        state = pr.append(c)
    assert state["rendered"] == "这是一段流式文本"
    assert state["render_count"] == 4
    print(f"   渲染{state['render_count']}次，结果：{state['rendered']}")

    print("\n✅ 流式输出测试通过")


if __name__ == "__main__":
    main()
