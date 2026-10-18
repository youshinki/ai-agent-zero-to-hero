# 第72篇配套代码：Agent成本精细化监控
# Token细粒度统计、用户用量审计、异常消耗拦截
# 运行：python 01_cost_monitoring.py

import json
from datetime import datetime, timedelta
from collections import defaultdict

# ========== Token成本跟踪器 ==========
class TokenCostTracker:
    """Token精细化统计"""
    
    PRICES = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
        "deepseek-chat": {"input": 0.0005, "output": 0.001},
        "claude-3": {"input": 0.015, "output": 0.075}
    }
    
    def __init__(self):
        self.records = []
        self.daily_stats = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "cost": 0, "calls": 0})
    
    def record_call(self, model, input_tokens, output_tokens, tenant_id="default", task_id="default", step="general"):
        """记录一次API调用"""
        prices = self.PRICES.get(model, {"input": 0.01, "output": 0.02})
        cost = (input_tokens / 1000) * prices["input"] + (output_tokens / 1000) * prices["output"]
        
        record = {
            "time": datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": round(cost, 6),
            "tenant_id": tenant_id,
            "task_id": task_id,
            "step": step
        }
        self.records.append(record)
        
        day = datetime.now().strftime("%Y-%m-%d")
        self.daily_stats[day]["input_tokens"] += input_tokens
        self.daily_stats[day]["output_tokens"] += output_tokens
        self.daily_stats[day]["cost"] += cost
        self.daily_stats[day]["calls"] += 1
        
        return record
    
    def get_tenant_usage(self, tenant_id):
        """按租户统计"""
        total_cost = 0
        total_tokens = 0
        for r in self.records:
            if r["tenant_id"] == tenant_id:
                total_cost += r["cost"]
                total_tokens += r["input_tokens"] + r["output_tokens"]
        return {"total_cost": round(total_cost, 4), "total_tokens": total_tokens, "calls": len([r for r in self.records if r["tenant_id"] == tenant_id])}
    
    def get_summary(self, days=7):
        """获取汇总"""
        total = {"cost": 0, "calls": 0, "tokens": 0}
        today = datetime.now()
        for i in range(days):
            day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            stats = self.daily_stats.get(day, {})
            total["cost"] += stats.get("cost", 0)
            total["calls"] += stats.get("calls", 0)
            total["tokens"] += stats.get("input_tokens", 0) + stats.get("output_tokens", 0)
        
        return {
            "period": f"{days}天",
            "total_cost": round(total["cost"], 2),
            "total_calls": total["calls"],
            "total_tokens": total["tokens"],
            "avg_daily_cost": round(total["cost"] / max(days, 1), 2),
            "avg_cost_per_call": round(total["cost"] / max(total["calls"], 1), 4)
        }

# ========== 异常消耗检测 ==========
class AnomalyDetector:
    """异常消耗检测"""
    
    def __init__(self):
        self.baselines = {}
        self.alerts = []
    
    def set_baseline(self, tenant_id, avg_daily_cost, max_daily_cost):
        """设置基线"""
        self.baselines[tenant_id] = {
            "avg_daily": avg_daily_cost,
            "max_daily": max_daily_cost
        }
    
    def check_anomaly(self, tenant_id, daily_cost):
        """检测异常"""
        baseline = self.baselines.get(tenant_id)
        if not baseline:
            return {"anomaly": False, "reason": "未设置基线"}
        
        issues = []
        if daily_cost > baseline["max_daily"]:
            issues.append(f"超出上限：{daily_cost:.2f} > {baseline['max_daily']:.2f}")
        if daily_cost > baseline["avg_daily"] * 3:
            issues.append(f"异常增长：日消耗是日均的{daily_cost/baseline['avg_daily']:.1f}倍")
        
        if issues:
            alert = {
                "tenant": tenant_id,
                "cost": daily_cost,
                "issues": issues,
                "time": datetime.now().isoformat(),
                "level": "critical" if daily_cost > baseline["max_daily"] * 2 else "warning"
            }
            self.alerts.append(alert)
            return {"anomaly": True, "alerts": [alert]}
        
        return {"anomaly": False}

# ========== 用量审计 ==========
class UsageAudit:
    """用户用量审计"""
    
    def __init__(self):
        self.user_usage = defaultdict(float)
        self.quotas = {}
    
    def set_quota(self, user_id, monthly_limit):
        """设置用户配额"""
        self.quotas[user_id] = monthly_limit
    
    def record_usage(self, user_id, cost):
        """记录用户用量"""
        self.user_usage[user_id] += cost
        
        quota = self.quotas.get(user_id, float('inf'))
        if self.user_usage[user_id] > quota:
            return {
                "exceeded": True,
                "usage": self.user_usage[user_id],
                "quota": quota,
                "overage": self.user_usage[user_id] - quota
            }
        return {"exceeded": False, "usage": self.user_usage[user_id], "quota": quota}
    
    def get_report(self):
        """生成用量报告"""
        report = []
        for user_id, usage in sorted(self.user_usage.items(), key=lambda x: x[1], reverse=True):
            report.append({
                "user": user_id,
                "total_usage": round(usage, 2),
                "quota": self.quotas.get(user_id, "不限"),
                "usage_rate": f"{usage/self.quotas[user_id]*100:.1f}%" if user_id in self.quotas else "N/A"
            })
        return report

if __name__ == "__main__":
    print("=" * 60)
    print("💰 Agent成本精细化监控")
    print("=" * 60)
    
    # 1. Token统计
    tracker = TokenCostTracker()
    print("\n1️⃣ Token调用记录")
    print("-" * 40)
    
    # 模拟API调用
    tracker.record_call("gpt-4", 500, 1000, "tenant_001", "task_01", "planning")
    tracker.record_call("gpt-3.5-turbo", 200, 400, "tenant_001", "task_01", "execution")
    tracker.record_call("gpt-4", 1000, 2000, "tenant_002", "task_02", "generation")
    tracker.record_call("deepseek-chat", 300, 600, "tenant_001", "task_03", "simple_qa")
    
    for r in tracker.records:
        print(f"  [{r['tenant_id']}] {r['model']}: {r['input_tokens']}入+{r['output_tokens']}出 = ¥{r['cost']:.6f}")
    
    # 2. 租户使用统计
    print("\n2️⃣ 租户用量统计")
    for tenant in ["tenant_001", "tenant_002"]:
        usage = tracker.get_tenant_usage(tenant)
        print(f"  {tenant}: {usage['calls']}次调用, {usage['total_tokens']}tokens, ¥{usage['total_cost']}")
    
    # 3. 汇总数据
    print("\n3️⃣ 汇总")
    summary = tracker.get_summary(7)
    for k, v in summary.items():
        print(f"  {k}: {v}")
    
    # 4. 异常检测
    print("\n4️⃣ 异常消耗检测")
    detector = AnomalyDetector()
    detector.set_baseline("tenant_001", avg_daily_cost=1.5, max_daily_cost=5.0)
    
    result = detector.check_anomaly("tenant_001", daily_cost=12.5)
    if result["anomaly"]:
        for alert in result["alerts"]:
            print(f"  🚨 [{alert['level']}] {alert['tenant']}: {alert['issues']}")
    else:
        print("  ✅ 无异常")
    
    # 5. 用户用量审计
    print("\n5️⃣ 用户用量审计")
    audit = UsageAudit()
    audit.set_quota("user_001", 50.0)
    audit.set_quota("user_002", 100.0)
    
    audit.record_usage("user_001", 30.0)
    audit.record_usage("user_001", 25.0)
    audit.record_usage("user_002", 80.0)
    
    report = audit.get_report()
    for r in report:
        status = "⚠️ 超配额" if r['usage_rate'] != "N/A" and float(r['usage_rate'].rstrip('%')) > 100 else "✅ 正常"
        print(f"  {r['user']}: ¥{r['total_usage']}/{r['quota']} ({r['usage_rate']}) {status}")
