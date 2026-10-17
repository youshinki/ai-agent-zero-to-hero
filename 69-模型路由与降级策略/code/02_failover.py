MODELS = {
    "premium": [{"name": "gpt-4o"}, {"name": "claude"}, {"name": "qwen-max"}],
    "fast":    [{"name": "gpt-4o-mini"}, {"name": "qwen-turbo"}],
}

def call_with_failover(query, level):
    for m in MODELS[level]:          # 按顺序尝试
        try:
            return call_model(m["name"], query, timeout=15)
        except (TimeoutError, RateLimitError, ServerError):
            log.warning(f"{m['name']} 失败，切换下一个")
            continue
    raise AllModelDown("所有模型都不可用")   # 兜底：返回友好话术
