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
