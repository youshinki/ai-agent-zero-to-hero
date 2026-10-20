# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 model_router/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

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
