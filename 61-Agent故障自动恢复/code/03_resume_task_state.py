# -*- coding: utf-8 -*-
# 状态机断点续跑：多步任务崩了从上次状态继续，不从头来
ORDER_FLOW = ["CREATED", "ORDER_QUERIED", "REFUNDED", "NOTIFIED", "DONE"]


def load_state(task_id):
    # 从数据库读上次走到哪了（占位）
    return {"current_step": "ORDER_QUERIED"}


def save_state(task_id, step):
    # 持久化当前状态（占位）
    pass


def refund(task_id):
    pass  # 占位：执行退款


def notify(task_id):
    pass  # 占位：补发通知


def resume_task(task_id):
    state = load_state(task_id)   # 从数据库读上次走到哪了
    step = state["current_step"]
    # 根据断点继续，不从头跑
    if step == "ORDER_QUERIED":
        refund(task_id)          # 已经查过订单了，直接退款
        save_state(task_id, "REFUNDED")
    if step == "REFUNDED":
        notify(task_id)          # 已经退过了，只补通知
        save_state(task_id, "NOTIFIED")
