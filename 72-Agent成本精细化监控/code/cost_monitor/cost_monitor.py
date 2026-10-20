#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第72篇配套完整项目代码 · cost_monitor.py
成本精细化监控：Token细粒度统计、用户用量审计、异常消耗拦截

  1. 多维度记账（租户/任务/环节/模型）
  2. 用量审计与配额
  3. 异常消耗检测（突增/超限/高频）
  4. 拦截策略
  5. 成本报表
==========================================================================
"""

import time
from collections import defaultdict
from typing import (Dict, List)


PRICES = {
    "gpt-4": {"in": 0.21, "out": 0.42},
    "deepseek-chat": {"in": 0.002, "out": 0.004},
    "qwen-turbo": {"in": 0.0015, "out": 0.003},
}


class CostMonitor:
    def __init__(self, daily_budget: float = 20.0,
                 alert_ratio: float = 0.8):
        self.daily_budget = daily_budget
        self.alert_ratio = alert_ratio
        
        self.records: List[Dict] = []
        self.by_tenant: Dict[str, Dict] = defaultdict(
            lambda: {"tokens_in": 0, "tokens_out": 0, "cost": 0.0,
                     "calls": 0})
        self.by_task: Dict[str, Dict] = defaultdict(
            lambda: {"tokens": 0, "cost": 0.0})
        self.by_step: Dict[str, Dict] = defaultdict(
            lambda: {"tokens": 0, "cost": 0.0})
        self.alerts: List[Dict] = []
        self.blocked = 0
        self.total_cost = 0.0
    
    # ---------------- 记账 ----------------
    @staticmethod
    def calc_cost(model: str, tin: int, tout: int) -> float:
        p = PRICES.get(model, PRICES["deepseek-chat"])
        return round(tin / 1000 * p["in"] + tout / 1000 * p["out"], 6)
    
    def record(self, tenant: str, task_id: str, step: str, model: str,
               tokens_in: int, tokens_out: int) -> Dict:
        cost = self.calc_cost(model, tokens_in, tokens_out)
        rec = {
            "time": time.time(), "tenant": tenant, "task": task_id,
            "step": step, "model": model,
            "tokens_in": tokens_in, "tokens_out": tokens_out,
            "cost": cost,
        }
        self.records.append(rec)
        self.total_cost = round(self.total_cost + cost, 6)
        
        t = self.by_tenant[tenant]
        t["tokens_in"] += tokens_in
        t["tokens_out"] += tokens_out
        t["cost"] = round(t["cost"] + cost, 6)
        t["calls"] += 1
        
        tk = self.by_task[task_id]
        tk["tokens"] += tokens_in + tokens_out
        tk["cost"] = round(tk["cost"] + cost, 6)
        
        st = self.by_step[step]
        st["tokens"] += tokens_in + tokens_out
        st["cost"] = round(st["cost"] + cost, 6)
        
        return rec
    
    # ---------------- 异常检测 ----------------
    def check_anomaly(self, tenant: str, tenant_quota: float = 5.0) -> List[Dict]:
        alerts = []
        info = self.by_tenant.get(tenant)
        if not info:
            return alerts
        
        # 1. 超租户配额
        if info["cost"] > tenant_quota:
            alerts.append({"type": "quota_exceeded", "tenant": tenant,
                           "cost": info["cost"], "quota": tenant_quota})
        # 2. 总量告警
        if self.total_cost > self.daily_budget * self.alert_ratio:
            alerts.append({"type": "budget_warning",
                           "total": round(self.total_cost, 4),
                           "budget": self.daily_budget})
        # 3. 单任务异常
        for task_id, tk in self.by_task.items():
            if tk["tokens"] > 50000:
                alerts.append({"type": "task_token_spike",
                               "task": task_id, "tokens": tk["tokens"]})
        
        self.alerts.extend(alerts)
        return alerts
    
    # ---------------- 拦截 ----------------
    def intercept(self, tenant: str, estimated_cost: float,
                  tenant_quota: float = 5.0) -> Dict:
        info = self.by_tenant.get(tenant, {"cost": 0.0})
        if info["cost"] + estimated_cost > tenant_quota:
            self.blocked += 1
            return {"allowed": False, "reason": "租户配额不足"}
        if self.total_cost + estimated_cost > self.daily_budget:
            self.blocked += 1
            return {"allowed": False, "reason": "全局预算不足"}
        return {"allowed": True}
    
    # ---------------- 报表 ----------------
    def report(self) -> Dict:
        return {
            "total_cost": round(self.total_cost, 4),
            "calls": len(self.records),
            "tenants": {k: {**v, "cost": round(v["cost"], 4)}
                        for k, v in self.by_tenant.items()},
            "top_tasks": sorted(self.by_task.items(),
                                key=lambda x: x[1]["cost"], reverse=True)[:3],
            "top_steps": sorted(self.by_step.items(),
                                key=lambda x: x[1]["cost"], reverse=True)[:3],
            "alerts": len(self.alerts),
            "blocked": self.blocked,
        }


def demo():
    print("=" * 66)
    print("💰 Agent 成本精细化监控演示")
    print("=" * 66)
    
    mon = CostMonitor(daily_budget=1.0, alert_ratio=0.5)
    
    print("\n[1] 多维度记账：")
    mon.record("tenant_a", "task_1", "plan", "gpt-4", 500, 200)
    mon.record("tenant_a", "task_1", "execute", "deepseek-chat", 300, 400)
    mon.record("tenant_b", "task_2", "plan", "deepseek-chat", 200, 100)
    mon.record("tenant_b", "task_2", "execute", "qwen-turbo", 800, 600)
    for r in mon.records:
        print(f"   {r['tenant']}/{r['task']}/{r['step']} {r['model']} "
              f"→ ¥{r['cost']}")
    
    print("\n[2] 异常检测：")
    alerts = mon.check_anomaly("tenant_a", tenant_quota=0.05)
    for a in alerts:
        print(f"   ⚠️ {a}")
    
    print("\n[3] 拦截：")
    print(f"   {mon.intercept('tenant_a', 0.5, tenant_quota=0.05)}")
    print(f"   {mon.intercept('tenant_b', 0.01, tenant_quota=5.0)}")
    
    print("\n[4] 报表：")
    rep = mon.report()
    print(f"   总成本：¥{rep['total_cost']}，调用{rep['calls']}次，"
          f"拦截{rep['blocked']}次")
    for t, info in rep["tenants"].items():
        print(f"   {t}：¥{info['cost']}（{info['calls']}次）")


if __name__ == "__main__":
    demo()
