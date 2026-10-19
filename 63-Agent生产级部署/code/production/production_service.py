#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第63篇配套完整项目代码 · production_service.py
Agent 生产级部署：服务隔离、并发控制、日志埋点、灰度上线

  1. 并发控制（信号量 / 限流）
  2. 服务隔离（业务与模型调用分离、超时）
  3. 结构化日志 + trace_id 链路
  4. 灰度路由（按权重/用户）
  5. 健康检查与优雅降级
==========================================================================
"""

import asyncio
import json
import random
import time
import uuid
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel


app = FastAPI(title="生产级 Agent 服务", version="1.0.0")


# ======================================================================
# 一、链路日志
# ======================================================================

class TraceLogger:
    def __init__(self):
        self.logs = []
    
    def log(self, trace_id: str, event: str, **fields):
        entry = {"ts": round(time.time(), 3), "trace_id": trace_id,
                 "event": event, **fields}
        self.logs.append(entry)
        print(json.dumps(entry, ensure_ascii=False))
        return entry
    
    def filter(self, trace_id: str):
        return [l for l in self.logs if l["trace_id"] == trace_id]


logger = TraceLogger()


# ======================================================================
# 二、并发控制
# ======================================================================

class ConcurrencyLimiter:
    def __init__(self, limit: int = 3):
        self.limit = limit
        self.sem = asyncio.Semaphore(limit)
        self.active = 0
        self.rejected = 0
    
    async def __aenter__(self):
        if self.active >= self.limit:
            self.rejected += 1
            raise HTTPException(status_code=429, detail="并发已满，请稍后重试")
        await self.sem.acquire()
        self.active += 1
        return self
    
    async def __aexit__(self, *args):
        self.active -= 1
        self.sem.release()


limiter = ConcurrencyLimiter(limit=3)


# ======================================================================
# 三、服务隔离 + 超时
# ======================================================================

class ModelService:
    """模型服务隔离层：统一超时、重试、降级"""
    
    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout
    
    async def call(self, prompt: str, version: str = "v1") -> str:
        async def _work():
            await asyncio.sleep(0.01)
            if version == "v2" and random.random() < 0.1:
                raise RuntimeError("v2 偶发失败")
            return f"[{version}] 针对「{prompt[:20]}」的回答"
        try:
            return await asyncio.wait_for(_work(), timeout=self.timeout)
        except asyncio.TimeoutError:
            return "（模型超时，已降级为默认回答）"
        except RuntimeError:
            return await self.call(prompt, "v1")  # 降级回v1
    
    # 业务侧不直接调用外部，隔离在此层


model_service = ModelService()


# ======================================================================
# 四、灰度路由
# ======================================================================

class CanaryRouter:
    def __init__(self, v2_weight: float = 0.2):
        self.v2_weight = v2_weight
        self.stats = {"v1": 0, "v2": 0}
    
    def route(self, user_id: str = "") -> str:
        # 白名单用户优先走v2
        if user_id.startswith("beta_"):
            self.stats["v2"] += 1
            return "v2"
        if random.random() < self.v2_weight:
            self.stats["v2"] += 1
            return "v2"
        self.stats["v1"] += 1
        return "v1"


router = CanaryRouter(v2_weight=0.2)


# ======================================================================
# 五、接口
# ======================================================================

class ChatRequest(BaseModel):
    task: str
    user_id: str = ""


@app.post("/api/chat")
async def chat(req: ChatRequest, x_trace_id: Optional[str] = Header(None)):
    trace_id = x_trace_id or uuid.uuid4().hex[:12]
    logger.log(trace_id, "request_start", task=req.task[:30])
    
    async with limiter:
        version = router.route(req.user_id)
        logger.log(trace_id, "route", version=version)
        try:
            answer = await model_service.call(req.task, version)
            logger.log(trace_id, "request_done", version=version,
                       answer_len=len(answer))
            return {"code": 0, "trace_id": trace_id, "version": version,
                    "answer": answer}
        except Exception as e:
            logger.log(trace_id, "request_error", error=str(e))
            return {"code": 3001, "trace_id": trace_id,
                    "answer": "服务繁忙，请稍后重试。"}


@app.get("/health")
async def health():
    return {"status": "ok", "active": limiter.active,
            "rejected": limiter.rejected, "canary": router.stats}


@app.get("/api/trace/{trace_id}")
async def trace(trace_id: str):
    return {"trace_id": trace_id, "logs": logger.filter(trace_id)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
