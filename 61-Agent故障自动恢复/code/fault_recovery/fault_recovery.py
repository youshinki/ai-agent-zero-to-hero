#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第61篇配套完整项目代码 · fault_recovery.py
Agent 故障自动恢复：异常捕获、重试策略、任务回滚

  1. 指数退避重试（带抖动）
  2. 熔断器（连续失败 → 短路）
  3. 断点续跑（checkpoint）
  4. 任务回滚（compensating actions）
  5. 降级兜底
==========================================================================
"""

import random
import time
from typing import Any, Callable, Dict, List, Optional


# ======================================================================
# 一、重试
# ======================================================================

class RetryPolicy:
    def __init__(self, max_attempts: int = 3, base_delay: float = 0.05,
                 max_delay: float = 1.0, jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
    
    def delay(self, attempt: int) -> float:
        d = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
        if self.jitter:
            d *= random.uniform(0.5, 1.0)
        return d
    
    def run(self, fn: Callable, *args, **kwargs) -> Dict:
        log = []
        for attempt in range(1, self.max_attempts + 1):
            try:
                result = fn(*args, **kwargs)
                log.append({"attempt": attempt, "ok": True})
                return {"ok": True, "result": result, "attempts": attempt,
                        "log": log}
            except Exception as e:
                log.append({"attempt": attempt, "ok": False, "error": str(e)})
                if attempt < self.max_attempts:
                    time.sleep(self.delay(attempt))
        return {"ok": False, "result": None, "attempts": self.max_attempts,
                "log": log}


# ======================================================================
# 二、熔断器
# ======================================================================

class CircuitBreaker:
    """CLOSED → (失败达阈值) OPEN → (超时) HALF_OPEN → 成功 CLOSED"""
    
    def __init__(self, failure_threshold: int = 3, recovery_time: float = 0.2):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.state = "CLOSED"
        self.opened_at = 0.0
    
    def allow(self) -> bool:
        if self.state == "OPEN":
            if time.time() - self.opened_at >= self.recovery_time:
                self.state = "HALF_OPEN"
                return True
            return False
        return True
    
    def success(self):
        self.failures = 0
        self.state = "CLOSED"
    
    def failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            self.opened_at = time.time()
    
    def call(self, fn: Callable, *args, **kwargs) -> Dict:
        if not self.allow():
            return {"ok": False, "error": "熔断中，快速失败", "state": self.state}
        try:
            result = fn(*args, **kwargs)
            self.success()
            return {"ok": True, "result": result, "state": self.state}
        except Exception as e:
            self.failure()
            return {"ok": False, "error": str(e), "state": self.state}


# ======================================================================
# 三、断点续跑
# ======================================================================

class Checkpoint:
    def __init__(self):
        self.store: Dict[str, Any] = {}
    
    def save(self, task_id: str, step: int, data: Any):
        self.store[task_id] = {"step": step, "data": data}
    
    def load(self, task_id: str) -> Optional[Dict]:
        return self.store.get(task_id)
    
    def clear(self, task_id: str):
        self.store.pop(task_id, None)


class ResumableTask:
    def __init__(self, steps: List[Callable], checkpoint: Checkpoint):
        self.steps = steps
        self.checkpoint = checkpoint
    
    def run(self, task_id: str) -> Dict:
        cp = self.checkpoint.load(task_id)
        start = cp["step"] + 1 if cp else 0
        results = list(cp["data"]) if cp else []
        
        for i in range(start, len(self.steps)):
            try:
                results.append(self.steps[i]())
                self.checkpoint.save(task_id, i, results)
            except Exception as e:
                return {"ok": False, "failed_step": i, "error": str(e),
                        "results": results}
        
        self.checkpoint.clear(task_id)
        return {"ok": True, "results": results}


# ======================================================================
# 四、任务回滚
# ======================================================================

class Transaction:
    """补偿事务：按逆序执行回滚动作"""
    
    def __init__(self):
        self.actions: List[Dict] = []
    
    def do(self, name: str, forward: Callable, compensate: Callable):
        try:
            result = forward()
            self.actions.append({"name": name, "compensate": compensate})
            return result
        except Exception as e:
            self.rollback()
            raise RuntimeError(f"{name} 失败，已回滚：{e}")
    
    def rollback(self) -> List[str]:
        done = []
        for action in reversed(self.actions):
            try:
                action["compensate"]()
                done.append(action["name"])
            except Exception:
                pass
        self.actions.clear()
        return done


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("🛟 Agent 故障自动恢复演示")
    print("=" * 66)
    
    print("\n[1] 重试：")
    rp = RetryPolicy(max_attempts=3)
    state = {"n": 0}
    def flaky():
        state["n"] += 1
        if state["n"] < 3:
            raise ValueError("临时失败")
        return "成功"
    r = rp.run(flaky)
    print(f"   结果：{r['result']}，尝试{r['attempts']}次")
    
    print("\n[2] 熔断：")
    cb = CircuitBreaker(failure_threshold=2, recovery_time=0.1)
    def always_fail():
        raise RuntimeError("上游故障")
    for i in range(3):
        r = cb.call(always_fail)
        print(f"   第{i+1}次：{r['state']}｜{r.get('error','')[:20]}")
    time.sleep(0.15)
    print(f"   恢复后允许：{cb.allow()}（state={cb.state}）")
    
    print("\n[3] 断点续跑：")
    cp = Checkpoint()
    steps = [
        lambda: "步骤1完成",
        lambda: "步骤2完成",
        lambda: "步骤3完成",
    ]
    rt = ResumableTask(steps, cp)
    r = rt.run("task_1")
    print(f"   全部完成：{r['ok']}，结果{len(r['results'])}个")
    
    # 模拟中途失败 → 续跑
    state2 = {"n": 0}
    def unstable():
        state2["n"] += 1
        if state2["n"] == 2:
            raise RuntimeError("第2步失败")
        return f"步骤{state2['n']}完成"
    rt2 = ResumableTask([unstable, unstable, unstable], cp)
    r2 = rt2.run("task_2")
    print(f"   中途失败：step={r2.get('failed_step')}，已完成{len(r2['results'])}步")
    r3 = rt2.run("task_2")
    print(f"   续跑结果：{r3['ok']}，共{len(r3['results'])}步")
    
    print("\n[4] 回滚：")
    tx = Transaction()
    log = []
    tx.do("创建文件", lambda: log.append("+file") or "ok",
          lambda: log.append("-file"))
    try:
        tx.do("写入内容", lambda: (_ for _ in ()).throw(RuntimeError("磁盘满")),
              lambda: log.append("-content"))
    except RuntimeError as e:
        print(f"   {e}")
    print(f"   操作日志：{log}")


if __name__ == "__main__":
    demo()
