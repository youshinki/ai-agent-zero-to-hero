#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第31篇配套 · test_cost.py
验证成本优化效果：
  1. 缓存命中（重复问题零成本）
  2. 模型路由（简单任务降级）
  3. 提示词压缩
  4. 预算熔断
  5. 综合节省率（目标 ≥50%）

运行: python test_cost.py
"""

from cost_optimizer import (
    TokenCounter,
    PromptCompressor,
    ModelRouter,
    BatchProcessor,
    BudgetGuard,
)
from commercial_service import OptimizedService


def main():
    print("=" * 68)
    print("🧪 商用成本极致优化测试")
    print("=" * 68)

    # 1. Token计量与成本
    print("\n[1] Token计量与成本：")
    text = "请帮我分析一下这份企业知识库的部署方案是否合理。"
    tokens = TokenCounter.estimate(text)
    print(f"   「{text}」→ 约{tokens} token")
    for model in ["gpt-4", "deepseek-chat", "qwen-turbo"]:
        print(f"   {model} 成本：¥{TokenCounter.cost(model, tokens, 100)}")

    # 2. 提示词压缩
    print("\n[2] 提示词压缩：")
    verbose = ("请注意，你是一个专业的AI助手，你需要非常重要地记住，请务必尽量全面地"
               "分析这个问题，非常非常重要。" * 3)
    compressed = PromptCompressor.compress(verbose)
    print(f"   压缩前：{len(verbose)}字 / 约{TokenCounter.estimate(verbose)}token")
    print(f"   压缩后：{len(compressed)}字 / 约{TokenCounter.estimate(compressed)}token")

    # 3. 模型路由
    print("\n[3] 模型路由：")
    cases = ["你好", "现在几点了？", "帮我分析一下这份复杂的架构方案，并结合历史数据给出优化建议"]
    for c in cases:
        print(f"   「{c[:20]}...」→ {ModelRouter.route(c)}")

    # 4. 批量合并
    print("\n[4] 批量合并：")
    items = [f"问题{i}" for i in range(1, 12)]
    batches = BatchProcessor.merge(items, size=5)
    print(f"   {len(items)}个问题 → {len(batches)}次请求")

    # 5. 综合优化演示
    print("\n[5] 综合优化演示（模拟100次请求）：")
    svc = OptimizedService()
    # 60%重复问题 + 30%简单问题 + 10%复杂问题
    questions = []
    for i in range(60):
        questions.append(f"公司的部署流程是什么？")  # 完全重复
    for i in range(30):
        questions.append(f"帮我翻译一下第{i}段文字")      # 简单任务
    for i in range(10):
        questions.append(f"请深度分析第{i}份业务报告并给出完整优化方案、风险评估和落地建议")

    for q in questions:
        svc.chat(q)

    report = svc.report()
    print(f"\n   调用次数：{report['calls']}（另有{60 - report['calls']}次命中缓存免调用）")
    print(f"   基线成本（全gpt-4）：¥{report['baseline_cost']}")
    print(f"   实际成本：¥{report['total_cost']}")
    print(f"   节省：¥{report['total_saved']}（{report['savings_rate']}）")
    print(f"   缓存命中率：{report['cache']['hit_rate']}")
    print(f"   预算状态：{report['budget']}")

    assert float(report["savings_rate"].rstrip("%")) >= 50, "综合节省率应≥50%"

    # 6. 预算熔断
    print("\n[6] 预算熔断测试：")
    guard = BudgetGuard(daily=0.01, monthly=100)
    guard.record(0.009)
    print(f"   已用¥0.009/预算¥0.01，新请求预估¥0.005 → 允许：{guard.check(0.005)}")
    assert guard.check(0.005) is False
    print(f"   拦截次数：{guard.stats()['blocked_requests']}")

    print("\n✅ 商用成本优化测试通过（节省率≥50%）")


if __name__ == "__main__":
    main()
