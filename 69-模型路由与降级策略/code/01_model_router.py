# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 model_router/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

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
