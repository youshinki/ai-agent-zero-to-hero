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
