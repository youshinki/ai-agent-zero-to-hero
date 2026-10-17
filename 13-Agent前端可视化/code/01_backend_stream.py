from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from agent_core import agent
import json
app = FastAPI(
    title="AI Agent 对话服务",
    description="前后端联调流式对话服务",
    version="1.1.0"
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
# 流式对话核心接口
@app.post("/api/agent/stream")
async def agent_stream_run(request: AgentRequest):
    try:
        result = agent.run(request.task)
        final_text = result["final_result"]
        # 逐字流式生成
        def stream_generator():
            for char in final_text:
                yield json.dumps({"char": char}, ensure_ascii=False) + "\n"
        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# 健康检测
@app.get("/health")
async def health_check():
    return {"code":200, "msg":"服务正常"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
