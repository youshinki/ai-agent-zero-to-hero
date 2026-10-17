# -*- coding: utf-8 -*-
# 最朴素的策略：窗口快满就删掉最早的一条历史
def count_tokens(messages) -> int:
    # 实际应调用 tokenizer（如 tiktoken）计数；这里占位
    return sum(len(m.get("content", "")) for m in messages)


def truncate_history(history, max_tokens=100000):
    while count_tokens(history) > max_tokens:
        history.pop(0)  # 删掉最早的一条
    return history
