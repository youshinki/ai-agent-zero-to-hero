# -*- coding: utf-8 -*-
# 状态机：只允许合法转移，拒绝跳步
#
# 状态流转示例：
# INIT -> COLLECT_ORDER -> VERIFY_ORDER -> CONFIRM -> REFUNDING -> DONE
# 任意状态 -> FAILED / CANCELLED

TRANSITIONS = {
    "INIT":          ["COLLECT_ORDER"],
    "COLLECT_ORDER": ["VERIFY_ORDER", "CANCELLED"],
    "VERIFY_ORDER":  ["CONFIRM", "COLLECT_ORDER", "FAILED"],
    "CONFIRM":       ["REFUNDING", "CANCELLED"],
    "REFUNDING":     ["DONE", "FAILED"],
}


def can_transit(current, target):
    return target in TRANSITIONS.get(current, [])


# 持久化的会话状态对象示例：
STATE_SAMPLE = {
    "session_id": "sess_001",
    "tenant_id": "client_a",
    "current_state": "COLLECT_ORDER",
    "context": {
        "order_id": "ORD-20240815",
        "reason": "商品破损",
    },
    "version": 3,                # 乐观锁版本号
    "updated_at": 1730000000,
}
