#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第61篇配套 · test_fault_recovery.py
"""

import time

from fault_recovery import (
    RetryPolicy, CircuitBreaker, Checkpoint, ResumableTask,
    Transaction, demo,
)


def main():
    print("=" * 66)
    print("🧪 故障自动恢复测试")
    print("=" * 66)

    print("\n[1] 重试：")
    rp = RetryPolicy(max_attempts=3, base_delay=0.01)
    n = {"v": 0}
    def flaky():
        n["v"] += 1
        if n["v"] < 3:
            raise ValueError("fail")
        return "ok"
    r = rp.run(flaky)
    assert r["ok"] and r["attempts"] == 3
    print(f"   3次后成功")

    r2 = rp.run(lambda: (_ for _ in ()).throw(ValueError("always")))
    assert not r2["ok"] and r2["attempts"] == 3
    print(f"   始终失败：{r2['attempts']}次后放弃")

    print("\n[2] 熔断：")
    cb = CircuitBreaker(failure_threshold=2, recovery_time=0.1)
    def fail():
        raise RuntimeError("err")
    r1 = cb.call(fail); r2 = cb.call(fail)
    assert cb.state == "OPEN"
    r3 = cb.call(fail)
    assert "熔断" in r3["error"]
    print(f"   连续失败后：{cb.state}")
    time.sleep(0.12)
    assert cb.allow() and cb.state == "HALF_OPEN"
    cb.success()
    assert cb.state == "CLOSED"
    print("   HALF_OPEN → 成功 → CLOSED")

    print("\n[3] 断点续跑：")
    cp = Checkpoint()
    rt = ResumableTask([lambda: "a", lambda: "b", lambda: "c"], cp)
    r = rt.run("t1")
    assert r["ok"] and len(r["results"]) == 3
    print("   完整执行3步")

    calls = {"n": 0}
    recovered = {"v": False}
    def step():
        calls["n"] += 1
        if calls["n"] == 2 and not recovered["v"]:
            raise RuntimeError("transient")
        return f"s{calls['n']}"
    rt2 = ResumableTask([step, step, step], cp)
    r = rt2.run("t2")
    assert not r["ok"] and r["failed_step"] == 1 and len(r["results"]) == 1
    print(f"   失败于step{r['failed_step']}，已完成{len(r['results'])}步")
    recovered["v"] = True  # 模拟故障恢复
    r = rt2.run("t2")
    assert r["ok"]
    print(f"   续跑完成：共{len(r['results'])}步")

    print("\n[4] 回滚：")
    tx = Transaction()
    log = []
    tx.do("A", lambda: log.append("+A"), lambda: log.append("-A"))
    try:
        tx.do("B", lambda: (_ for _ in ()).throw(RuntimeError("B失败")),
              lambda: log.append("-B"))
    except RuntimeError:
        pass
    assert "-A" in log
    print(f"   回滚日志：{log}")

    print("\n[5] 演示：")
    demo()
    print("\n✅ 故障恢复测试通过")


if __name__ == "__main__":
    main()
