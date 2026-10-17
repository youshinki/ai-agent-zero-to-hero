def run_worker():
    while True:
        task = task_queue.dequeue()
        update_status(task["task_id"], "RUNNING", progress=10)
        try:
            for step in run_long_agent(task):   # 长任务分阶段
                update_status(task["task_id"],
                              progress=step.progress)
            update_status(task["task_id"], "DONE",
                          result=step.result)
        except Exception as e:
            update_status(task["task_id"], "FAILED", error=str(e))
