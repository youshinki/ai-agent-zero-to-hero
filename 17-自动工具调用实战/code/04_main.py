# ===== main.py：工具调用详情接口 =====

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from agent_core import agent
from memory_utils import compress_history
from scheduler_task import start_scheduler
import json
import os

app = FastAPI(title="自动工具调用Agent服务", version="5.0 自主执行版")

start_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEMORY_DIR = "chat_memory"
MEMORY_FILE = os.path.join(MEMORY_DIR, "history.json")
os.makedirs(MEMORY_DIR, exist_ok=True)

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

class ChatRequest(BaseModel):
    task: str
    history: list

class ToolUseRequest(BaseModel):
    task: str
    history: list

@app.post("/api/agent/stream")
async def stream_chat(req: ChatRequest):
    try:
        compressed_hist = compress_history(req.history)
        result = agent.run(req.task, compressed_hist)
        final_text = result["final_answer"]

        req.history.append({"role": "user", "content": req.task})
        req.history.append({"role": "assistant", "content": final_text})

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(req.history, f, ensure_ascii=False, indent=2)

        def stream():
            for char in final_text:
                yield json.dumps({"char": char}, ensure_ascii=False) + "\n"
        return StreamingResponse(stream(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.get("/api/agent/history")
async def get_history():
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"code": 200, "history": data}

@app.post("/api/agent/clear")
async def clear_history():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
    return {"code": 200, "msg": "记忆已清空"}

@app.get("/health")
async def health():
    return {"code": 200, "msg": "自动工具调用Agent服务正常运行"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
