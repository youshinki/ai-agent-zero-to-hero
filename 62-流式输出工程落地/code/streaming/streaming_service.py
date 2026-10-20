#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第62篇配套完整项目代码 · streaming_service.py
流式输出工程落地：SSE / WebSocket、局部渲染、中断控制

  1. SSE 逐字/逐块输出
  2. WebSocket 双向流
  3. 中断控制（cancel token）
  4. 局部渲染（chunk 组装）
  5. 心跳与错误帧
==========================================================================
"""

import asyncio
import json
import time
from typing import (AsyncGenerator, Dict, Optional)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


app = FastAPI(title="流式输出服务", version="1.0.0")


# ======================================================================
# 一、生成器
# ======================================================================

def mock_answer(task: str) -> str:
    return f"这是针对「{task}」的回答：分三步完成。第一步分析需求；第二步执行；第三步自检并交付。"


async def sse_generator(task: str, chunk_size: int = 4,
                        cancel: Optional[Dict] = None) -> AsyncGenerator[str, None]:
    """SSE 事件流：逐块输出，支持中断"""
    text = mock_answer(task)
    seq = 0
    for i in range(0, len(text), chunk_size):
        if cancel and cancel.get("cancelled"):
            yield f"event: cancelled\ndata: {json.dumps({'reason': 'client_cancel'}, ensure_ascii=False)}\n\n"
            return
        chunk = text[i:i + chunk_size]
        seq += 1
        payload = {"seq": seq, "chunk": chunk, "done": False}
        yield f"event: chunk\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.001)
    yield f"event: done\ndata: {json.dumps({'seq': seq + 1, 'done': True, 'total': len(text)}, ensure_ascii=False)}\n\n"


class ChatRequest(BaseModel):
    task: str
    chunk_size: int = 4


# ======================================================================
# 二、SSE 接口
# ======================================================================

@app.post("/api/stream/sse")
async def stream_sse(req: ChatRequest):
    return StreamingResponse(
        sse_generator(req.task, req.chunk_size),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ======================================================================
# 三、WebSocket 接口
# ======================================================================

@app.websocket("/ws/stream")
async def ws_stream(ws: WebSocket):
    await ws.accept()
    cancel = {"cancelled": False}
    try:
        while True:
            data = await ws.receive_json()
            action = data.get("action", "ask")
            
            if action == "cancel":
                cancel["cancelled"] = True
                await ws.send_json({"event": "cancelled"})
                continue
            
            task = data.get("task", "")
            cancel["cancelled"] = False
            text = mock_answer(task)
            for i in range(0, len(text), 4):
                if cancel["cancelled"]:
                    await ws.send_json({"event": "cancelled"})
                    break
                await ws.send_json({"event": "chunk", "chunk": text[i:i+4]})
                await asyncio.sleep(0)
            else:
                await ws.send_json({"event": "done", "total": len(text)})
    except WebSocketDisconnect:
        pass


# ======================================================================
# 四、局部渲染（前端逻辑模拟）
# ======================================================================

class PartialRenderer:
    """模拟前端：只更新变化的部分，避免整页重绘"""
    
    def __init__(self):
        self.buffer = ""
        self.renders = 0
    
    def append(self, chunk: str) -> Dict:
        self.buffer += chunk
        self.renders += 1
        return {"rendered": self.buffer, "render_count": self.renders,
                "delta": chunk}


# ======================================================================
# 五、心跳
# ======================================================================

async def heartbeat(interval: float = 5.0) -> AsyncGenerator[str, None]:
    while True:
        yield f"event: ping\ndata: {int(time.time())}\n\n"
        await asyncio.sleep(interval)


@app.get("/health")
async def health():
    return {"status": "ok", "sse": "/api/stream/sse", "ws": "/ws/stream"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
