#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第69篇配套 · test_model_router.py
"""

import random

from model_router import (
    MODELS, FAILOVER_CHAIN, ModelRouter, CircuitBreaker,
    RobustRouter, demo,
)


def main():
    print("=" * 66)
    print("🧪 模型路由与降级测试")
    print("=" * 66)

    print("\n[1] 策略路由：")
    assert ModelRouter("quality").pick() == "gpt-4"
    assert ModelRouter("cost").pick() == "qwen-turbo"
    assert ModelRouter("latency").pick() == "qwen-turbo"
    print("   ✅ quality→gpt-4，cost/latency→qwen-turbo")

    print("\n[2] 复杂度：")
    r = ModelRouter("balanced")
    assert r.pick("low") == "qwen-turbo"
    print(f"   low→{r.pick('low')}，high→{r.pick('high')}")

    print("\n[3] 健康度：")
    r.health["gpt-4"] = False
    assert r.pick("high") != "gpt-4"
    print("   ✅ 不健康模型被跳过")

    print("\n[4] failover：")
    r = ModelRouter()
    nxt = r.failover("gpt-4")
    assert nxt == "deepseek-chat"
    nxt = r.failover("deepseek-chat")
    assert nxt == "qwen-turbo"
    print("   ✅ gpt-4→deepseek→qwen")

    print("\n[5] 熔断器：")
    cb = CircuitBreaker(threshold=2, recovery=0.1)
    assert cb.allow()
    cb.failure(); cb.failure()
    assert not cb.allow()
    import time
    time.sleep(0.12)
    assert cb.allow()
    print("   ✅ 熔断 → 恢复")

    print("\n[6] 主备自动切换：")
    random.seed(7)
    rr = RobustRouter()
    out = rr.call("测试", "high")
    assert out["ok"] or out["tried"]
    print(f"   结果：model={out.get('model')} tried={out['tried']}")

    # 全部失败
    class AlwaysFail(RobustRouter):
        def _invoke(self, model, prompt):
            raise TimeoutError("all fail")
    af = AlwaysFail()
    out = af.call("x")
    assert not out["ok"]
    print(f"   全失败：{out['error']}，尝试{out['tried']}")

    print("\n[7] 演示：")
    random.seed(1)
    demo()
    print("\n✅ 模型路由测试通过")


if __name__ == "__main__":
    main()
