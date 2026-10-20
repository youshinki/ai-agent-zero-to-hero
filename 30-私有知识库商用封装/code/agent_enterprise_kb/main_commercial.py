#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第30篇配套完整项目代码 · main_commercial.py
企业商用启动入口：
  隐私拦截 + 商用输出封装 + 批量入库 + 知识库管理
==========================================================================
"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from knowledge_base.core.kb_core import kb
from knowledge_base.commercial.commercial_wrapper import commercial_agent
from knowledge_base.commercial.batch_upload import batch_uploader
from knowledge_base.commercial.safe_privacy import commercial_privacy


app = FastAPI(title="企业私有知识库问答系统（商用版）", version="1.0.0 交付版")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


class ChatRequest(BaseModel):
    task: str


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """商用问答接口（隐私拦截 + 干净输出）"""
    if not commercial_privacy.forbid_external_leak(req.task):
        return {"success": False, "answer": commercial_privacy.leak_response()}
    
    result = commercial_agent.safe_answer(req.task)
    result["answer"] = commercial_privacy.mask_output(result["answer"])
    return result


@app.post("/api/kb/batch_import")
async def batch_import():
    return batch_uploader.batch_import_all()


@app.get("/api/kb/stats")
async def kb_stats():
    return {"code": 200, "stats": kb.stats()}


@app.post("/api/kb/clear")
async def kb_clear():
    return {"code": 200, "msg": batch_uploader.clear_docs()}


@app.get("/api/privacy/status")
async def privacy_status():
    return {"privacy_mode": commercial_privacy.privacy_mode}


@app.get("/health")
async def health():
    return {"code": 200, "msg": "企业商用服务运行正常", "privacy_mode": commercial_privacy.privacy_mode}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
