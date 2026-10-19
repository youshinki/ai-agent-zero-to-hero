#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第15篇配套 · test_compress.py
验证智能记忆压缩：构造长历史 → 压缩 → Token大幅下降且保留关键信息

运行: python test_compress.py
"""

from memory_utils import (
    count_message_tokens, compress_history,
    compression_stats, build_context,
)
from config import COMPRESS_THRESHOLD, KEEP_RECENT


def build_long_history(turns: int = 30):
    """构造模拟长对话历史"""
    history = []
    history.append({"role": "user", "content": "我是一名AI开发者，擅长Agent工程化，偏好结果先行的表达风格。"})
    history.append({"role": "assistant", "content": "好的，已记住你的身份和偏好。"})
    for i in range(turns):
        history.append({"role": "user", "content": f"第{i+1}个问题：请帮我分析一下AI Agent在场景{i+1}中的应用价值，并给出结论。"})
        history.append({"role": "assistant", "content": f"结论：场景{i+1}适合采用Agent方案，核心收益是降本提效，建议先小范围验证。"})
    return history


def main():
    print("=" * 62)
    print("🧪 智能记忆压缩测试")
    print("=" * 62)
    print(f"参数：COMPRESS_THRESHOLD={COMPRESS_THRESHOLD}  KEEP_RECENT={KEEP_RECENT}")

    history = build_long_history(30)
    print(f"\n构造历史：{len(history)} 条消息")

    before_tokens = count_message_tokens(history)
    print(f"压缩前估算 token：{before_tokens}")

    compressed = compress_history(history)
    after_tokens = count_message_tokens(compressed)
    print(f"压缩后消息数：{len(compressed)} 条")
    print(f"压缩后估算 token：{after_tokens}")

    stats = compression_stats(history)
    print(f"\n📊 压缩统计：")
    for k, v in stats.items():
        print(f"   {k}: {v}")

    # 检查关键信息保留
    print(f"\n🔍 关键信息保留检查：")
    all_text = "\n".join(m.get("content", "") for m in compressed)
    checks = {
        "身份(AI开发者)": "AI开发者" in all_text,
        "偏好(结果先行)": "结果先行" in all_text,
        "摘要标记": "【历史对话摘要】" in all_text,
        "保留近期完整对话": any("第30个问题" in m.get("content", "") for m in compressed),
    }
    for name, ok in checks.items():
        print(f"   {'✅' if ok else '❌'} {name}")

    # 压缩后的上下文预览
    print(f"\n📄 压缩后上下文预览（前400字）：")
    ctx = build_context(compressed)
    print("   " + ctx[:400].replace("\n", "\n   "))

    # 断言
    assert len(compressed) < len(history), "压缩后条数应减少"
    assert stats["tokens_after"] < stats["tokens_before"], "压缩后token应下降"
    assert checks["摘要标记"], "应包含摘要"
    print("\n✅ 智能记忆压缩测试通过")


if __name__ == "__main__":
    main()
