# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 cost_monitor/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

def call_model(model, messages, tenant_id, task_id, step):
    resp = client.chat.completions.create(model=model, messages=messages)
    usage = resp.usage
    # 按 租户+任务+环节 维度记账
    redis.hincrby(f"cost:{tenant_id}:{month()}", "tokens_in", usage.prompt_tokens)
    redis.hincrby(f"cost:{tenant_id}:{month()}", "tokens_out", usage.completion_tokens)
    log.info("token_usage",
             tenant_id=tenant_id, task_id=task_id, step=step,
             model=model, tokens_in=usage.prompt_tokens, tokens_out=usage.completion_tokens)
    return resp.choices[0].message.content
