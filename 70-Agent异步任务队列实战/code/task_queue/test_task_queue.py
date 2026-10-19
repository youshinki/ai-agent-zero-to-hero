#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第70篇配套 · test_task_queue.py
"""

import time

from task_queue import Task, TaskQueue, demo


def main():
    print("=" * 66)
    print("🧪 异步任务队列测试")
    print("=" * 66)

    q = TaskQueue(worker_count=2)

    def fast(task, progress):
        for i in range(5):
            time.sleep(0.002)
            progress((i + 1) * 20)
        return f"done:{task.payload['payload']}"

    def flaky(task, progress):
        if task.retries == 0:
            raise RuntimeError("首次失败")
        return "retry-ok"

    q.register_handler("fast", fast)
    q.register_handler("flaky", flaky)
    q.start()

    print("\n[1] 提交与执行：")
    ids = [q.submit("fast", i) for i in range(3)]
    time.sleep(0.15)
    for tid in ids:
        t = q.get(tid)
        assert t["status"] == "done" and t["progress"] == 100
        print(f"   {tid}: {t['status']} → {t['result']}")

    print("\n[2] 进度回调：")
    t = q.get(ids[0])
    assert "elapsed_ms" in t
    print(f"   耗时：{t['elapsed_ms']}ms")

    print("\n[3] 重试：")
    tid = q.submit("flaky", "x", max_retry=1)
    time.sleep(0.1)
    t = q.get(tid)
    assert t["status"] == "done" and t["retries"] == 1
    print(f"   重试{t['retries']}次后成功：{t['result']}")

    print("\n[4] 失败：")
    tid = q.submit("unknown_kind", "x")
    time.sleep(0.1)
    t = q.get(tid)
    assert t["status"] == "failed" and "未注册" in t["error"]
    print(f"   {t['error']}")

    print("\n[5] 取消：")
    tid = q.submit("fast", "cancel-me")
    q.cancel(tid)
    time.sleep(0.05)
    t = q.get(tid)
    assert t["status"] in ("cancelled", "done")
    print(f"   状态：{t['status']}")

    print("\n[6] 超时清理：")
    t2 = Task("t_timeout", {"kind": "fast", "payload": 0}, timeout=0.001)
    t2.status = Task.RUNNING
    t2.started = time.time() - 5
    q.tasks["t_timeout"] = t2
    expired = q.cleanup_timeouts()
    assert "t_timeout" in expired
    assert q.get("t_timeout")["status"] == "failed"
    print(f"   清理：{expired}")

    print("\n[7] 统计：")
    s = q.stats()
    assert s["total"] >= 5
    print(f"   {s}")

    q.stop()

    print("\n[8] 演示：")
    demo()
    print("\n✅ 异步任务队列测试通过")


if __name__ == "__main__":
    main()
