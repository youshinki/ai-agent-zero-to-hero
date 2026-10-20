# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 task_queue/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

@app.post("/longtask")
def submit_longtask(query: str, tenant_id: str):
    task_id = uuid.uuid4().hex[:12]
    # 任务入队，并初始化状态
    task_queue.enqueue({
        "task_id": task_id,
        "tenant_id": tenant_id,
        "query": query,
        "status": "QUEUED",
        "progress": 0
    })
    return {"task_id": task_id}   # 立刻返回，不等执行
