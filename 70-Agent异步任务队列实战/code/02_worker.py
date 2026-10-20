# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 task_queue/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

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
