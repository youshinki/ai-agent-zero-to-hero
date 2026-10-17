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
