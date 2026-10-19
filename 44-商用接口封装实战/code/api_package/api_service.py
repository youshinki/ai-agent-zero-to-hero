#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第44篇配套完整项目代码 · api_service.py
商用接口封装：
  1. API 版本化（/api/v1）
  2. 统一入参/出参/错误码
  3. API Key 鉴权
  4. 限流（令牌桶）
  5. 分页、用量统计、健康检查
  6. Python SDK

运行: python api_service.py      # 或 uvicorn api_service:app
测试: python test_api.py
"""

import time
import uuid
from collections import defaultdict
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel


# ======================================================================
# 一、错误码规范
# ======================================================================

ERROR_CODES = {
    0: "成功",
    1001: "认证失败（API Key 无效）",
    1002: "请求过于频繁（触发限流）",
    2001: "参数错误",
    3001: "处理异常",
    4001: "上游服务错误",
}


# ======================================================================
# 二、统一响应
# ======================================================================

def ok(data: Any = None, msg: str = "请求成功", trace_id: str = "") -> Dict:
    return {"code": 0, "msg": msg, "data": data,
            "trace_id": trace_id or uuid.uuid4().hex[:12]}


def fail(code: int, msg: str = "", trace_id: str = "") -> Dict:
    return {"code": code, "msg": msg or ERROR_CODES.get(code, "未知错误"),
            "data": None, "trace_id": trace_id or uuid.uuid4().hex[:12]}


# ======================================================================
# 三、鉴权与限流
# ======================================================================

class Auth:
    def __init__(self, keys=None):
        # demo keys；生产从配置/数据库读取
        self.keys = keys or {"sk-demo-001": "tenant_a", "sk-demo-002": "tenant_b"}
    
    def verify(self, api_key: str) -> Optional[str]:
        return self.keys.get(api_key)


class RateLimiter:
    """令牌桶：每个租户每分钟 N 次"""
    
    def __init__(self, rate_per_minute: int = 60):
        self.rate = rate_per_minute
        self.buckets: Dict[str, Dict] = defaultdict(
            lambda: {"tokens": rate_per_minute, "last": time.time()}
        )
    
    def allow(self, tenant: str) -> bool:
        b = self.buckets[tenant]
        now = time.time()
        elapsed = now - b["last"]
        # 按时间补充令牌
        b["tokens"] = min(self.rate, b["tokens"] + elapsed * (self.rate / 60))
        b["last"] = now
        if b["tokens"] >= 1:
            b["tokens"] -= 1
            return True
        return False


# ======================================================================
# 四、用量统计
# ======================================================================

class UsageMeter:
    def __init__(self):
        self.usage = defaultdict(lambda: {"requests": 0, "tokens_in": 0,
                                          "tokens_out": 0})
    
    def record(self, tenant: str, tokens_in: int, tokens_out: int):
        u = self.usage[tenant]
        u["requests"] += 1
        u["tokens_in"] += tokens_in
        u["tokens_out"] += tokens_out
    
    def get(self, tenant: str) -> Dict:
        return dict(self.usage.get(tenant, {"requests": 0,
                                           "tokens_in": 0, "tokens_out": 0}))


# ======================================================================
# 五、FastAPI 应用
# ======================================================================

app = FastAPI(title="AI Agent 商用 API", version="1.0.0")

auth = Auth()
limiter = RateLimiter()
meter = UsageMeter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = ""


class PageQuery(BaseModel):
    page: int = 1
    size: int = 20


def _check(api_key: str) -> str:
    tenant = auth.verify(api_key) if api_key else None
    if not tenant:
        raise HTTPException(
            status_code=401,
            detail=fail(1001),
        )
    if not limiter.allow(tenant):
        raise HTTPException(
            status_code=429,
            detail=fail(1002),
        )
    return tenant


@app.get("/health")
async def health():
    return ok({"status": "healthy", "version": "1.0.0"})


@app.post("/api/v1/chat")
async def chat(req: ChatRequest, x_api_key: Optional[str] = Header(None, alias="X-Api-Key")):
    tenant = _check(x_api_key)
    try:
        if not req.message.strip():
            return fail(2001, "message 不能为空")
        answer = f"针对「{req.message[:40]}」的回答（tenant={tenant}）"
        tokens_in = max(1, len(req.message) // 2)
        tokens_out = max(1, len(answer) // 2)
        meter.record(tenant, tokens_in, tokens_out)
        return ok({"answer": answer, "session_id": req.session_id,
                   "usage": {"tokens_in": tokens_in, "tokens_out": tokens_out}})
    except Exception as e:
        return fail(3001, f"处理异常：{e}")


@app.get("/api/v1/usage")
async def usage(x_api_key: Optional[str] = Header(None, alias="X-Api-Key")):
    tenant = _check(x_api_key)
    return ok(meter.get(tenant))


@app.get("/api/v1/docs/items")
async def list_items(page: int = Query(1, ge=1),
                     size: int = Query(20, ge=1, le=100),
                     x_api_key: Optional[str] = Header(None, alias="X-Api-Key")):
    """演示分页接口"""
    tenant = _check(x_api_key)
    all_items = [{"id": i, "name": f"doc_{i}"} for i in range(1, 56)]
    start = (page - 1) * size
    return ok({
        "items": all_items[start:start + size],
        "page": page, "size": size, "total": len(all_items),
        "total_pages": (len(all_items) + size - 1) // size,
    })


# ======================================================================
# 六、Python SDK
# ======================================================================

class AgentSDK:
    """商用 SDK：统一封装请求与错误处理
    
    transport 可注入（如 TestClient），便于测试。
    """
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000",
                 transport=None):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.transport = transport  # 有则用（如 TestClient），否则用 requests
    
    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.base_url}{path}"
        headers = {"X-Api-Key": self.api_key}
        if self.transport is not None:
            r = self.transport.post(path, json=payload, headers=headers)
            return r.json()
        import requests
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        return r.json()
    
    def _get(self, path: str, params: dict = None) -> dict:
        if self.transport is not None:
            r = self.transport.get(path, params=params,
                                   headers={"X-Api-Key": self.api_key})
            return r.json()
        import requests
        r = requests.get(f"{self.base_url}{path}", params=params,
                         headers={"X-Api-Key": self.api_key}, timeout=30)
        return r.json()
    
    def chat(self, message: str, session_id: str = "") -> dict:
        return self._post("/api/v1/chat",
                          {"message": message, "session_id": session_id})
    
    def usage(self) -> dict:
        return self._get("/api/v1/usage")
    
    def list_items(self, page: int = 1, size: int = 20) -> dict:
        return self._get("/api/v1/docs/items", {"page": page, "size": size})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
