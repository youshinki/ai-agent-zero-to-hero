#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第13篇配套完整项目代码 · main.py
前后端联调流式对话服务（FastAPI + SSE逐字推送）
==========================================================================

启动: python main.py
文档: http://127.0.0.1:8000/docs
前端: 浏览器打开 index.html
==========================================================================
"""

import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from agent_core import agent
from config import HOST, PORT


app = FastAPI(
    title="AI Agent 对话服务",
    description="前后端联调流式对话服务",
    version="1.1.0",
)

# 解决前端跨域（必须配置）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentRequest(BaseModel):
    task: str


@app.post("/api/agent/stream")
async def agent_stream_run(request: AgentRequest):
    """流式对话核心接口：逐字推送，实现打字机效果"""
    try:
        result = agent.run(request.task)
        final_text = result["final_result"]

        def stream_generator():
            for char in final_text:
                yield json.dumps({"char": char}, ensure_ascii=False) + "\n"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"code": 200, "msg": "服务正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
