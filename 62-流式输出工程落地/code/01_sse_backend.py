# -*- coding: utf-8 -*-
# 后端 SSE 最小示例：边生成边推 + 客户端断开即停
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json

app = FastAPI()


@app.post("/chat/stream")
async def chat_stream(query: str):
    async def event_generator():
        # 先推一个状态：正在思考
        yield f"data: {json.dumps({'type': 'status', 'text': '正在检索知识库...'})}\n\n"

        # 调大模型，开启 stream=True，逐 chunk 拿结果
        async for chunk in llm.astream(query):  # noqa: F821（占位：模型客户端）
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield f"data: {json.dumps({'type': 'answer', 'text': delta})}\n\n"

        # 最后推一个结束标记
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# 关键：每生成一个 chunk 前检查客户端是否已断开，断开就立刻停止，不再烧 Token
async def event_generator_with_cancel(request: Request, query: str):
    async for chunk in llm.astream(query):  # noqa: F821
        if await request.is_disconnected():
            break   # 用户已断开，立刻停止，不再浪费 Token
        yield chunk
