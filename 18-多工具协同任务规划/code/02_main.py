# ===== main.py：适配多工具协同 =====

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import StreamingResponse
# 升级为多工具协同Agent
from agent_core import agent
from memory_utils import compress_history
from scheduler_task import start_scheduler
import json
import os

app = FastAPI(title="多工具协同AI Agent", version="6.0 自主规划版")

# 启动定时任务服务
start_scheduler()

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 记忆文件配置
MEMORY_DIR = "chat_memory"
MEMORY_FILE = os.path.join(MEMORY_DIR, "history.json")
os.makedirs(MEMORY_DIR, exist_ok=True)

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# 请求模型
class ChatRequest(BaseModel):
    task: str
    history: list

class ToolUseRequest(BaseModel):
    task: str
    history: list

# 流式对话接口（兼容旧版）
@app.post("/api/agent/stream")
async def stream_chat(req: ChatRequest):
    try:
        compressed_hist = compress_history(req.history)
        result = agent.run(req.task, compressed_hist)
        final_text = result["final_answer"]

        # 保存对话记忆
        req.history.append({"role": "user", "content": req.task})
        req.history.append({"role": "assistant", "content": final_text})
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(req.history, f, ensure_ascii=False, indent=2)

        # 流式输出
        def stream():
            for char in final_text:
                yield json.dumps({"char": char}, ensure_ascii=False) + "\n"
        return StreamingResponse(stream(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 工具调用详情接口（新增多步骤日志返回）
@app.post("/api/agent/tool-use")
async def tool_use_chat(req: ToolUseRequest):
    try:
        compressed_hist = compress_history(req.history)
        result = agent.run(req.task, compressed_hist)

        req.history.append({"role": "user", "content": req.task})
        req.history.append({"role": "assistant", "content": result["final_answer"]})
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(req.history, f, ensure_ascii=False, indent=2)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 历史记忆接口
@app.get("/api/agent/history")
async def get_history():
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"code": 200, "history": data}

# 清空记忆接口
@app.post("/api/agent/clear")
async def clear_history():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
    return {"code": 200, "msg": "记忆已清空"}

# 服务健康检测
@app.get("/health")
async def health():
    return {"code": 200, "msg": "多工具协同Agent服务正常运行"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
