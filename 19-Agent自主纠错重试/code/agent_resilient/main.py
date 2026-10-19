#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第19篇配套 · main.py（容错版Agent服务）"""

import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from agent_core import agent
from memory_utils import compress_history
from scheduler_task import start_scheduler
from config import HOST, PORT, MEMORY_DIR, MEMORY_FILE


app = FastAPI(title="自主纠错重试Agent服务", version="7.0 容错版")
start_scheduler()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


def _ensure_memory():
    os.makedirs(MEMORY_DIR, exist_ok=True)
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def _load() -> list:
    _ensure_memory()
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save(history: list):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


class ChatRequest(BaseModel):
    task: str
    history: list = []


@app.post("/api/agent/stream")
async def stream_chat(req: ChatRequest):
    try:
        result = agent.run(req.task, compress_history(req.history))
        final_text = result["final_answer"]
        full = list(req.history) + [
            {"role": "user", "content": req.task},
            {"role": "assistant", "content": final_text},
        ]
        _save(full)

        def stream():
            for char in final_text:
                yield json.dumps({"char": char}, ensure_ascii=False) + "\n"

        return StreamingResponse(stream(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/tool-use")
async def tool_use(req: ChatRequest):
    try:
        result = agent.run(req.task, compress_history(req.history))
        full = list(req.history) + [
            {"role": "user", "content": req.task},
            {"role": "assistant", "content": result["final_answer"]},
        ]
        _save(full)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agent/history")
async def history():
    return {"code": 200, "history": _load()}


@app.post("/api/agent/clear")
async def clear():
    _save([])
    return {"code": 200, "msg": "记忆已清空"}


@app.get("/health")
async def health():
    return {"code": 200, "msg": "容错版Agent服务正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
