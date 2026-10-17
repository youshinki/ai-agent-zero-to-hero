# -*- coding: utf-8 -*-
# 结构化消息 + 子任务超时兜底
import json
import time
import concurrent.futures


def send_message(to_agent, msg_type, payload):
    return {
        "from": "orchestrator",
        "to": to_agent,
        "type": msg_type,
        "payload": payload,
        "ts": int(time.time()),
    }


def run_with_timeout(func, args, timeout=30):
    """子任务超时兜底，防止单个Agent卡死全流程"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(func, *args)
        try:
            return fut.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            return {"error": "timeout", "message": "子Agent执行超时，请重试或转人工"}
