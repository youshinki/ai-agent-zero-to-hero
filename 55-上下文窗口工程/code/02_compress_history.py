# -*- coding: utf-8 -*-
# 进阶策略：把前 N 轮对话压缩成摘要，而不是直接删
def llm_summarize(old_part) -> str:
    # 调用大模型生成摘要，此处为占位
    return "（之前对话摘要：用户问了 A，查了 B，结果是 C）"


def compress_history(history, threshold=50):
    if len(history) > threshold:
        # 压缩前一半
        old_part = history[: threshold // 2]
        summary = llm_summarize(old_part)
        # 用摘要替换掉原来的 N 轮对话
        history = [{"role": "system", "content": f"之前的对话摘要：{summary}"}] + history[threshold // 2 :]
    return history
