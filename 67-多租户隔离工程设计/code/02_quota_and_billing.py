def check_quota(tenant_id):
    used = redis.get(f"token:{tenant_id}") or 0
    limit = plan_quota(tenant_id)   # 按套餐返回额度
    if used >= limit:
        raise QuotaExceeded("本月额度已用完，请升级套餐")
    return True

# ---- 下一段 ----

def record_usage(tenant_id, tokens_in, tokens_out, tool_calls):
    redis.hincrby(f"usage:{tenant_id}:{month()}", "tokens_in", tokens_in)
    redis.hincrby(f"usage:{tenant_id}:{month()}", "tool_calls", tool_calls)
    # 月底汇总即账单，超额按量计费或触发限流
