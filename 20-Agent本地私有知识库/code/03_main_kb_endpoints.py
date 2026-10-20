# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 agent_private_kb/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

# ===== main.py：知识库相关接口 =====

# 知识库相关接口
@app.post("/api/kb/upload")
async def kb_upload(file_path: str):
    res = kb_upload_doc(file_path)
    return {"code": 200, "msg": res}

@app.post("/api/kb/query")
async def kb_query(query: str):
    res = kb_search_query(query)
    return {"code": 200, "data": res}

@app.post("/api/kb/clear")
async def api_kb_clear():
    res = kb_clear()
    return {"code": 200, "msg": res}
