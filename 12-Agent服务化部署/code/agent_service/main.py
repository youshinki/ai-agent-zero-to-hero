#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第12篇配套完整项目代码 · main.py
全新API服务入口（FastAPI）

启动:
  cd agent_service
  python main.py
  # 或：uvicorn main:app --host 0.0.0.0 --port 8000

接口文档: http://127.0.0.1:8000/docs
==========================================================================
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict

from agent_core import agent
from config import HOST, PORT


# 初始化FastAPI服务
app = FastAPI(
    title="AI Agent 通用服务接口",
    description="基于规划-执行-反思闭环的通用智能体API服务",
    version="1.0.0",
)

# 跨域配置（支持前端网页直接调用 —— 文章可扩展方向1）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 标准化入参
class AgentRequest(BaseModel):
    task: str


# 标准化返回
def ok(data: Any = None, msg: str = "请求成功") -> Dict:
    return {"code": 200, "msg": msg, "data": data}


# ---------------- 核心接口 ----------------
@app.post("/api/agent/run")
async def agent_run(request: AgentRequest):
    """通用AI Agent任务执行接口"""
    try:
        result = agent.run(request.task)
        return ok(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务执行失败：{e}")


# ---------------- 健康检测 ----------------
@app.get("/health")
async def health_check():
    return {"code": 200, "msg": "服务正常运行", "status": "online"}


@app.get("/")
async def root():
    return {
        "service": "AI Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": ["/api/agent/run", "/health"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
