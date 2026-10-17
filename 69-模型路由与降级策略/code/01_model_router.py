ROUTER_PROMPT = """判断下面这个用户问题的复杂度，只输出一个词：
- simple: 查订单、问政策、简单事实问答
- complex: 需要多步推理、综合多个文档、写长文、分析
问题：{query}"""

def route_model(query):
    level = cheap_llm(ROUTER_PROMPT.format(query=query))  # 极便宜模型分诊
    if level.strip() == "complex":
        return PREMIUM_MODEL      # 复杂问题用旗舰
    return FAST_MODEL             # 简单问题用便宜快速模型

def answer(query):
    model = route_model(query)
    return call_model(model, query)
