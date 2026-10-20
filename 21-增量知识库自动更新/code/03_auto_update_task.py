# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 agent_incremental_kb/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

# ===== 定时任务：自动增量更新知识库 =====

from knowledge_base.kb_core import kb

def auto_kb_update_task():
    """定时自动增量更新知识库"""
    kb.scan_all_update()

def start_scheduler():
    scheduler.add_job(
        auto_kb_update_task,
        "cron",
        hour=3,
        minute=0,
        id="auto_kb_update",
        replace_existing=True
    )
