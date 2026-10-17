# -*- coding: utf-8 -*-
# 并发控制：信号量限流 + 队列满快速失败
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
semaphore = asyncio.Semaphore(10)   # 同时最多处理 10 个请求


@app.post("/chat")
async def chat(query: str, session_id: str):
    try:
        async with semaphore:        # 拿不到就排队
            return await run_agent(query, session_id)  # noqa: F821
    except asyncio.QueueFull:
        return JSONResponse({"error": "系统繁忙，请稍后再试"}, status_code=429)
