#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第14篇配套完整项目代码 · main.py
记忆版AI Agent服务：
  - 流式对话（带历史）
  - 自动读写 JSON 持久化
  - 读取历史 / 清空记忆 / 健康检测
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
from config import HOST, PORT, MEMORY_DIR, MEMORY_FILE, MAX_HISTORY_TURNS


app = FastAPI(title="记忆版AI Agent服务", version="2.0")

# 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
# 记忆存储层（本地JSON持久化）
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
    # 限制最大轮数，防止无限膨胀
    if len(history) > MAX_HISTORY_TURNS * 2:
        history = history[-MAX_HISTORY_TURNS * 2:]
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# ----------------------------------------------------------------------
# 请求模型
# ----------------------------------------------------------------------

class ChatRequest(BaseModel):
    task: str
    history: list = []


# ----------------------------------------------------------------------
# 接口
# ----------------------------------------------------------------------

@app.post("/api/agent/stream")
async def stream_chat(req: ChatRequest):
    """流式对话 + 自动保存记忆"""
    try:
        result = agent.run_with_history(req.task, req.history)
        final_text = result["final_result"]

        # 持久化写入本地JSON
        new_history = list(req.history)
        new_history.append({"role": "user", "content": req.task})
        new_history.append({"role": "assistant", "content": final_text})
        save_memory(new_history)

        def stream():
            for char in final_text:
                yield json.dumps({"char": char}, ensure_ascii=False) + "\n"

        return StreamingResponse(stream(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agent/history")
async def get_history():
    """读取历史记忆"""
    return {"code": 200, "history": load_memory()}


@app.post("/api/agent/clear")
async def clear_history():
    """清空记忆"""
    save_memory([])
    return {"code": 200, "msg": "记忆已清空"}


@app.get("/health")
async def health():
    return {"code": 200, "msg": "记忆版Agent服务正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
