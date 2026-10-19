#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第16篇配套完整项目代码 · main.py
全自动AI Agent服务（v4.0 主动智能版）：
  - 流式对话 + 记忆压缩持久化
  - 启动即常驻定时任务
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
from memory_utils import compress_history
from scheduler_task import start_scheduler, list_jobs, daily_auto_review, weekly_summary
from config import HOST, PORT, MEMORY_DIR, MEMORY_FILE


app = FastAPI(title="全自动AI Agent服务", version="4.0 主动智能版")

# 启动定时任务（全局只启动一次）
start_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
# 记忆存储
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
# 对话接口
# ----------------------------------------------------------------------

@app.post("/api/agent/stream")
async def stream_chat(req: ChatRequest):
    try:
        compressed_hist = compress_history(req.history)
        result = agent.run_with_history(req.task, compressed_hist)
        final_text = result["final_result"]

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


@app.post("/api/agent/clear")
async def clear_history():
    save_memory([])
    return {"code": 200, "msg": "记忆已清空"}


# ----------------------------------------------------------------------
# 定时任务管理接口（手动触发 + 状态查询）
# ----------------------------------------------------------------------

@app.get("/api/agent/jobs")
async def get_jobs():
    return {"code": 200, "jobs": list_jobs()}


@app.post("/api/agent/jobs/daily")
async def trigger_daily():
    """手动触发一次每日复盘（便于测试，不必等到22:30）"""
    result = daily_auto_review()
    return {"code": 200, "msg": "每日复盘已执行", "result": result}


@app.post("/api/agent/jobs/weekly")
async def trigger_weekly():
    """手动触发一次每周总结"""
    result = weekly_summary()
    return {"code": 200, "msg": "每周总结已执行", "result": result}


@app.get("/health")
async def health():
    return {"code": 200, "msg": "全自动Agent服务正常运行"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
