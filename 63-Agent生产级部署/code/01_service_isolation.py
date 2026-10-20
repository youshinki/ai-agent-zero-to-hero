# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 production/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

# -*- coding: utf-8 -*-
# 服务隔离：状态按 session_id 隔离 + 向量库按 tenant_id 过滤
from fastapi import FastAPI

app = FastAPI()


# ❌ 错误：全局变量，多用户直接串数据
# current_user_state = {}
#
# @app.post("/chat")
# async def chat(query: str):
#     current_user_state["history"].append(query)  # 所有人共用这一份

# ✅ 正确：状态按 session_id 隔离
@app.post("/chat")
async def chat(query: str, session_id: str):
    state = load_session(session_id)      # 从 Redis/数据库读该会话专属状态
    state["history"].append(query)
    save_session(session_id, state)       # noqa: F821（占位：持久化函数）
    return state


def load_session(session_id: str):
    return {"history": []}  # 占位


def search_kb(query, tenant_id):
    # 数据级隔离：每条文档带 tenant_id，检索时强制过滤
    return vector_store.search(  # noqa: F821（占位：向量库句柄）
        query,
        top_k=5,
        filter={"tenant_id": tenant_id},   # 必加，否则召回别人的文档
    )
