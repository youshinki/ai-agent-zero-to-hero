#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第54篇配套 · test_function_calling.py
"""

import json

from function_calling import (
    TOOLS, SchemaValidator, ToolRuntime, MockModel,
    FunctionCallAgent, demo,
)


def main():
    print("=" * 66)
    print("🧪 Function Calling 测试")
    print("=" * 66)

    print("\n[1] Schema：")
    assert len(TOOLS) == 2
    names = [t["function"]["name"] for t in TOOLS]
    assert names == ["get_weather", "calculator"]
    print(f"   ✅ {names}")

    print("\n[2] 校验：")
    v = SchemaValidator()
    assert v.validate("get_weather", {"city": "北京"})["valid"]
    assert not v.validate("get_weather", {})["valid"]          # 缺必填
    assert not v.validate("get_weather", {"city": 1})["valid"]  # 类型错
    assert not v.validate("get_weather", {"city": "北京", "unit": "x"})["valid"]  # enum
    assert not v.validate("nope", {})["valid"]                 # 未知工具
    print("   ✅ 必填/类型/enum/未知工具 校验通过")

    print("\n[3] 运行时：")
    rt = ToolRuntime()
    assert "22" in rt.get_weather("北京")
    assert "72" in rt.get_weather("北京", "f") or "71" in rt.get_weather("北京", "f")
    assert "576" in rt.calculator("(128+64)*3")
    assert "非法" in rt.calculator("__import__('os')")
    print("   ✅ 天气/计算/非法表达式")

    print("\n[4] 模型决策：")
    calls = MockModel.decide("北京天气")
    assert calls[0]["name"] == "get_weather"
    calls = MockModel.decide("计算 1+2")
    assert calls[0]["name"] == "calculator"
    assert MockModel.decide("你好") == []
    print("   ✅ 天气/计算/无需工具")

    print("\n[5] 完整闭环：")
    agent = FunctionCallAgent()
    r = agent.run("北京天气怎么样")
    assert r["tools_used"] == ["get_weather"] and "22" in r["answer"]
    r = agent.run("计算 (128+64)*3")
    assert "576" in r["answer"]
    r = agent.run("你好")
    assert r["tools_used"] == []
    print("   ✅ 完整问答闭环")

    print("\n[6] 参数错误兜底：")
    import function_calling as fc
    original = MockModel.decide
    MockModel.decide = staticmethod(lambda q: [
        {"name": "calculator", "arguments": "{bad json"}])
    r = agent.run("x")
    assert r["errors"] and "解析失败" in r["errors"][0]
    MockModel.decide = original
    print(f"   ✅ {r['errors'][0]}")

    print("\n[7] 演示：")
    demo()
    print("\n✅ Function Calling 测试通过")


if __name__ == "__main__":
    main()
