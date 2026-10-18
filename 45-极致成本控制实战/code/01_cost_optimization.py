# 第45篇配套代码：极致成本控制实战
# API计费节流优化，拉高纯利润
# 运行：python 01_cost_optimization.py

import json
from collections import defaultdict

# ========== 成本统计 ==========
class CostTracker:
    """Token用量与成本跟踪"""
    
    PRICES = {
        "gpt-4": {"input": 0.03, "output": 0.06},    # 每1K token
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
        "deepseek-chat": {"input": 0.0005, "output": 0.001},
        "text-embedding-ada-002": {"input": 0.0001, "output": 0.0001}
    }
    
    def __init__(self):
        self.daily_stats = defaultdict(lambda: {"requests": 0, "input_tokens": 0, "output_tokens": 0})
    
    def record(self, model, input_tokens, output_tokens):
        from datetime import datetime
        day = datetime.now().strftime("%Y-%m-%d")
        self.daily_stats[day]["requests"] += 1
        self.daily_stats[day]["input_tokens"] += input_tokens
        self.daily_stats[day]["output_tokens"] += output_tokens
    
    def calculate_cost(self, model, input_tokens, output_tokens):
        prices = self.PRICES.get(model, {"input": 0.01, "output": 0.02})
        input_cost = (input_tokens / 1000) * prices["input"]
        output_cost = (output_tokens / 1000) * prices["output"]
        return round(input_cost + output_cost, 4)
    
    def get_summary(self):
        total_cost = 0
        for day, stats in self.daily_stats.items():
            cost = self.calculate_cost("gpt-4", stats["input_tokens"], stats["output_tokens"])
            total_cost += cost
        return {
            "total_days": len(self.daily_stats),
            "total_cost": round(total_cost, 2),
            "avg_daily_cost": round(total_cost / max(len(self.daily_stats), 1), 2)
        }

# ========== 成本优化策略 ==========
class CostOptimizer:
    """成本优化方案"""
    
    @staticmethod
    def optimize_model_selection(task_type):
        """智能模型选择策略"""
        model_map = {
            "简单问答": {"model": "deepseek-chat", "cost_per_1k": 0.0005},
            "知识库检索": {"model": "text-embedding-ada-002", "cost_per_1k": 0.0001},
            "内容生成": {"model": "gpt-3.5-turbo", "cost_per_1k": 0.001},
            "复杂推理": {"model": "gpt-4", "cost_per_1k": 0.03},
            "代码生成": {"model": "deepseek-chat", "cost_per_1k": 0.0005}
        }
        return model_map.get(task_type, {"model": "gpt-3.5-turbo", "cost_per_1k": 0.001})
    
    @staticmethod
    def optimize_prompt(prompt):
        """Prompt优化：压缩token"""
        # 去重空格
        optimized = " ".join(prompt.split())
        # 去除冗余说明词
        redundancies = ["请注意", "请记住", "你是一个", "你是一位"]
        for word in redundancies:
            optimized = optimized.replace(word, "")
        return optimized
    
    @staticmethod
    def cache_strategy():
        """缓存策略"""
        return {
            "embedding缓存": "相同文本的embedding缓存24小时，减少重复API调用",
            "搜索结果缓存": "相同query的检索结果缓存1小时",
            "模型回复缓存": "精确匹配的问题直接返回缓存（适合FAQ场景）",
            "上下文缓存": "系统提示词/角色设定只发送一次，不重复计入"
        }

# ========== 成本对比 ==========
class CostComparison:
    """成本对比"""
    
    @staticmethod
    def compare_models():
        """不同模型成本对比"""
        scenarios = [
            {"name": "日常对话（1K+2K token）", "daily_calls": 1000},
            {"name": "知识库检索（0.5K+1K token）", "daily_calls": 5000},
            {"name": "内容生成（2K+8K token）", "daily_calls": 200},
        ]
        
        models = ["gpt-4", "gpt-3.5-turbo", "deepseek-chat"]
        prices = CostTracker.PRICES
        
        for s in scenarios:
            print(f"\n📊 {s['name']}（每日{s['daily_calls']}次）")
            for m in models:
                p = prices[m]
                cost = ((s['daily_calls'] * p['input'] * 1) + (s['daily_calls'] * p['output'] * 2)) / 1000
                print(f"  {m}: ¥{cost:.2f}/天 = ¥{cost*30:.2f}/月")

if __name__ == "__main__":
    print("=" * 60)
    print("💰 极致成本控制实战")
    print("=" * 60)
    
    tracker = CostTracker()
    tracker.record("gpt-4", 500, 1000)
    tracker.record("gpt-4", 300, 800)
    tracker.record("gpt-3.5-turbo", 200, 400)
    
    print("\n📊 单次调用成本")
    print("-" * 40)
    test_cases = [
        ("gpt-4", 500, 1000),
        ("gpt-3.5-turbo", 500, 1000),
        ("deepseek-chat", 500, 1000)
    ]
    for model, inp, out in test_cases:
        cost = tracker.calculate_cost(model, inp, out)
        print(f"  {model}: {inp}入+{out}出 → ¥{cost}")
    
    print("\n💰 成本对比")
    print("-" * 40)
    CostComparison.compare_models()
    
    print("\n🎯 智能模型选择")
    print("-" * 40)
    tasks = ["简单问答", "复杂推理", "内容生成", "知识库检索"]
    for t in tasks:
        rec = CostOptimizer.optimize_model_selection(t)
        print(f"  {t} → 推荐 {rec['model']}（¥{rec['cost_per_1k']}/1K token）")
    
    print("\n💡 优化策略")
    print("-" * 40)
    print("  • Prompt压缩（减少50%输入token）")
    for k, v in CostOptimizer.cache_strategy().items():
        print(f"  • {k}：{v}")
    print("  • 模型降级（简单任务用便宜模型）")
    print("  • 批量处理（合并请求减少API调用）")
