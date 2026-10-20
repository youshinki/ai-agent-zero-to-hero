# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 state_machine/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

# -*- coding: utf-8 -*-
# 脏状态清理：扫描卡死的僵尸会话，对账后归档
import time


def reconcile(state):
    # 查外部系统真实状态后修正（占位）
    return state


def archive_to_db(state):
    # 归档到数据库（占位）
    pass


def sweep_stale_sessions():
    stale = redis.keys("sess:*")  # noqa: F821 扫描所有会话（redis 句柄占位）
    for key in stale:
        state = load_state(key)   # noqa: F821
        # 卡在中间状态超过 30 分钟
        if state["current_state"] not in ["DONE", "CANCELLED", "FAILED"] \
           and time.time() - state["updated_at"] > 1800:
            reconcile(state)      # 查外部系统真实状态后修正
            archive_to_db(state)
            redis.delete(key)     # noqa: F821
