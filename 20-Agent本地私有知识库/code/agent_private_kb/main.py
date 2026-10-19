#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第20篇配套完整项目代码 · main.py
私有知识库Agent服务（含知识库管理接口）
==========================================================================
"""

import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from agent_core import agent
from memory_utils import compress_history
from knowledge_base.kb_core import kb
from scheduler_task import start_scheduler
from config import HOST, PORT, MEMORY_DIR, MEMORY_FILE


app = FastAPI(title="私有知识库Agent服务", version="8.0 私有大脑版")
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


class KBUploadRequest(BaseModel):
    file_path: str


class KBSearchRequest(BaseModel):
    query: str
    top_k: int = 3


# ---------------- 对话 ----------------

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


# ---------------- 知识库管理 ----------------

@app.post("/api/kb/upload")
async def kb_upload(req: KBUploadRequest):
    if not os.path.exists(req.file_path):
        raise HTTPException(status_code=404, detail=f"文件不存在：{req.file_path}")
    return {"code": 200, "msg": kb.add_doc_file(req.file_path)}


@app.post("/api/kb/search")
async def kb_search(req: KBSearchRequest):
    hits = kb.search(req.query, top_k=req.top_k)
    return {"code": 200, "results": hits}


@app.get("/api/kb/stats")
async def kb_stats():
    return {"code": 200, "stats": kb.stats()}


@app.post("/api/kb/clear")
async def kb_clear():
    return {"code": 200, "msg": kb.clear_kb()}


@app.get("/api/agent/history")
async def history():
    return {"code": 200, "history": _load()}


@app.post("/api/agent/clear")
async def clear():
    _save([])
    return {"code": 200, "msg": "记忆已清空"}


@app.get("/health")
async def health():
    return {"code": 200, "msg": "私有知识库Agent服务正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
