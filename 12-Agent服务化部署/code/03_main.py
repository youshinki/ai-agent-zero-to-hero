from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent_core import agent

# 初始化FastAPI服务
app = FastAPI(
    title="AI Agent 通用服务接口",
    description="基于规划-执行-反思闭环的通用智能体API服务",
    version="1.0.0"
)

# 定义请求参数模型（标准化入参）
class AgentRequest(BaseModel):
    task: str

# 定义核心Agent问答接口
@app.post("/api/agent/run")
async def agent_run(request: AgentRequest):
    """
    通用AI Agent任务执行接口
    传入用户任务，返回完整思考、执行、优化结果
    """
    try:
        # 调用Agent完整闭环
        result = agent.run(request.task)
        return {
            "code": 200,
            "msg": "请求成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务执行失败：{str(e)}")

# 健康检测接口（服务存活校验）
@app.get("/health")
async def health_check():
    return {"code": 200, "msg": "服务正常运行", "status": "online"}

if __name__ == "__main__":
    import uvicorn
    # 启动服务：0.0.0.0允许外网访问，端口8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
