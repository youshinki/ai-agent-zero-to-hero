#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第15篇配套完整项目代码 · main.py
无限记忆AI Agent服务（v3.0）：
  - 流式对话
  - 自动压缩后送入模型
  - 磁盘保存完整原始记录（压缩只用于推理）
==========================================================================

启动: python main.py
前端: 浏览器打开 index.html
==========================================================================
"""

import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from agent_core import agent
from memory_utils import compress_history, compression_stats
from config import HOST, PORT, MEMORY_DIR, MEMORY_FILE


app = FastAPI(title="无限记忆AI Agent服务", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
# 记忆存储（磁盘保存完整原始记录）
# ----------------------------------------------------------------------

def _ensure_memory_file():
    os.makedirs(MEMORY_DIR, exist_ok=True)
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def load_memory() -> list:
    _ensure_memory_file()
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_memory(history: list):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


class ChatRequest(BaseModel):
    task: str
    history: list = []


# ----------------------------------------------------------------------
# 接口
# ----------------------------------------------------------------------

@app.post("/api/agent/stream")
async def stream_chat(req: ChatRequest):
    try:
        # 压缩后的历史用于推理
        compressed_hist = compress_history(req.history)
        result = agent.run_with_history(req.task, compressed_hist)
        final_text = result["final_result"]

        # 磁盘保存完整原始记录（不压缩，保留全部细节）
        full_history = list(req.history)
        full_history.append({"role": "user", "content": req.task})
        full_history.append({"role": "assistant", "content": final_text})
        save_memory(full_history)

        def stream():
            for char in final_text:
                yield json.dumps({"char": char}, ensure_ascii=False) + "\n"

        return StreamingResponse(stream(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agent/history")
async def get_history():
    return {"code": 200, "history": load_memory()}


@app.get("/api/agent/compress_stats")
async def get_compress_stats():
    """查看当前记忆的压缩效果"""
    return {"code": 200, "stats": compression_stats(load_memory())}


@app.post("/api/agent/clear")
async def clear_history():
    save_memory([])
    return {"code": 200, "msg": "记忆已清空"}


@app.get("/health")
async def health():
    return {"code": 200, "msg": "无限记忆Agent服务正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
