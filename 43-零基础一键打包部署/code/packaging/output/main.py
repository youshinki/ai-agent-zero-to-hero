#!/usr/bin/env python3
"""启动入口（生产模式）"""
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 确保打包后能找到本地模块
if getattr(sys, "frozen", False):
    base = os.path.dirname(sys.executable)
    sys.path.insert(0, base)

app = FastAPI(title="AI Agent 服务", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "running", "service": "AI Agent"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/chat")
async def chat(payload: dict):
    task = payload.get("task", "")
    if not task:
        return {"success": False, "answer": "请输入问题。"}
    return {"success": True, "answer": f"已收到问题：{task}（示例实现）"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"服务启动：http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
