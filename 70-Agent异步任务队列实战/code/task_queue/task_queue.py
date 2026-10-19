#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第70篇配套完整项目代码 · task_queue.py
Agent 异步任务队列：长耗时任务后台排队、进度回调、超时清理

  1. 任务队列（提交/状态查询/结果获取）
  2. 后台 Worker（并发消费）
  3. 进度回调
  4. 超时清理与重试
  5. 取消任务
==========================================================================
"""

import threading
import time
import uuid
from collections import deque
from typing import Any, Callable, Dict, List, Optional


# ======================================================================
# 一、任务模型
# ======================================================================

class Task:
    PENDING, RUNNING, DONE, FAILED, CANCELLED = (
        "pending", "running", "done", "failed", "cancelled")
    
    def __init__(self, task_id: str, payload: Any,
                 timeout: float = 30.0, max_retry: int = 1):
        self.task_id = task_id
        self.payload = payload
        self.timeout = timeout
        self.max_retry = max_retry
        self.retries = 0
        self.status = self.PENDING
        self.progress = 0
        self.result: Any = None
        self.error: str = ""
        self.created = time.time()
        self.started = 0.0
        self.finished = 0.0
        self.cancel_requested = False
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id, "status": self.status,
            "progress": self.progress, "result": self.result,
            "error": self.error, "retries": self.retries,
            "elapsed_ms": round(((self.finished or time.time()) -
                                 (self.started or self.created)) * 1000, 1),
        }


# ======================================================================
# 二、队列
# ======================================================================

class TaskQueue:
    def __init__(self, worker_count: int = 2):
        self.tasks: Dict[str, Task] = {}
        self.queue: deque = deque()
        self.lock = threading.Lock()
        self.worker_count = worker_count
        self.handlers: Dict[str, Callable] = {}
        self.stop_flag = False
        self.workers: List[threading.Thread] = []
    
    def register_handler(self, name: str, fn: Callable):
        """fn(task, progress_callback) -> result"""
        self.handlers[name] = fn
    
    def submit(self, kind: str, payload: Any, timeout: float = 30.0,
               max_retry: int = 1) -> str:
        task_id = uuid.uuid4().hex[:10]
        task = Task(task_id, {"kind": kind, "payload": payload},
                    timeout, max_retry)
        with self.lock:
            self.tasks[task_id] = task
            self.queue.append(task_id)
        return task_id
    
    def get(self, task_id: str) -> Optional[Dict]:
        t = self.tasks.get(task_id)
        return t.to_dict() if t else None
    
    def cancel(self, task_id: str) -> bool:
        t = self.tasks.get(task_id)
        if not t:
            return False
        t.cancel_requested = True
        if t.status == Task.PENDING:
            t.status = Task.CANCELLED
        return True
    
    def start(self):
        self.stop_flag = False
        for i in range(self.worker_count):
            th = threading.Thread(target=self._worker, args=(i,), daemon=True)
            th.start()
            self.workers.append(th)
    
    def stop(self):
        self.stop_flag = True
        for th in self.workers:
            th.join(timeout=1)
        self.workers.clear()
    
    def _worker(self, worker_id: int):
        while not self.stop_flag:
            try:
                with self.lock:
                    if not self.queue:
                        task_id = None
                    else:
                        task_id = self.queue.popleft()
                if not task_id:
                    time.sleep(0.01)
                    continue
                self._run_task(self.tasks[task_id])
            except Exception:
                continue
    
    def _run_task(self, task: Task):
        if task.cancel_requested:
            task.status = Task.CANCELLED
            return
        task.status = Task.RUNNING
        task.started = time.time()
        kind = task.payload["kind"]
        handler = self.handlers.get(kind)
        if not handler:
            task.status = Task.FAILED
            task.error = f"未注册处理器：{kind}"
            task.finished = time.time()
            return
        
        def progress(p: int):
            task.progress = max(0, min(100, p))
        
        try:
            result = handler(task, progress)
            if task.cancel_requested:
                task.status = Task.CANCELLED
            else:
                task.status = Task.DONE
                task.result = result
                task.progress = 100
        except Exception as e:
            task.error = str(e)
            if task.retries < task.max_retry and not task.cancel_requested:
                task.retries += 1
                task.status = Task.PENDING
                with self.lock:
                    self.queue.append(task.task_id)
            else:
                task.status = Task.FAILED
        finally:
            task.finished = time.time()
    
    # ---------------- 超时清理 ----------------
    def cleanup_timeouts(self, now: Optional[float] = None) -> List[str]:
        now = now or time.time()
        expired = []
        for t in self.tasks.values():
            if t.status == Task.RUNNING and now - t.started > t.timeout:
                t.status = Task.FAILED
                t.error = "任务超时"
                t.finished = now
                expired.append(t.task_id)
        return expired
    
    def stats(self) -> Dict:
        counts: Dict[str, int] = {}
        for t in self.tasks.values():
            counts[t.status] = counts.get(t.status, 0) + 1
        return {"total": len(self.tasks), "queue_size": len(self.queue),
                "by_status": counts}


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("📬 Agent 异步任务队列演示")
    print("=" * 66)
    
    q = TaskQueue(worker_count=2)
    
    def long_task(task: Task, progress: Callable):
        total = 10
        for i in range(total):
            if task.cancel_requested:
                raise RuntimeError("cancelled")
            time.sleep(0.005)
            progress(int((i + 1) / total * 100))
        return f"完成长任务：{task.payload['payload']}"
    
    q.register_handler("long", long_task)
    q.start()
    
    ids = [q.submit("long", f"任务{i}") for i in range(5)]
    time.sleep(0.4)
    
    print("\n[1] 任务状态：")
    for tid in ids:
        t = q.get(tid)
        print(f"   {tid}: {t['status']} {t['progress']}%")
    
    print(f"\n[2] 队列统计：{q.stats()}")
    
    print("\n[3] 取消任务：")
    tid = q.submit("long", "可取消任务")
    q.cancel(tid)
    time.sleep(0.1)
    print(f"   取消后：{q.get(tid)['status']}")
    
    print("\n[4] 超时清理：")
    t2 = Task("timeout_task", {"kind": "long", "payload": "x"}, timeout=0.001)
    t2.status = Task.RUNNING
    t2.started = time.time() - 10
    q.tasks["timeout_task"] = t2
    expired = q.cleanup_timeouts()
    print(f"   超时任务：{expired}")
    
    q.stop()
    assert all(q.get(i)["status"] == "done" for i in ids)


if __name__ == "__main__":
    demo()
