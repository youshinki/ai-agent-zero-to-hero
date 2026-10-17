# 模拟大模型调用（通用接口）
def llm_call(prompt):
    # 此处替换为你的真实大模型API调用
    return "模型原始输出结果"

# 1. 第一轮：常规任务执行
def agent_execute(user_input):
    base_prompt = f"请完成用户任务：{user_input}"
    return llm_call(base_prompt)

# 2. 第二轮：反射自查纠错
def agent_reflect(user_input, raw_result):
    reflect_prompt = f"""
    你现在是任务审核专家，请严格自查本次任务全过程，输出纠错报告：
    用户原始需求：{user_input}
    你的原始输出：{raw_result}

    请从以下维度逐条自查：
    1. 是否存在事实幻觉、虚假信息
    2. 是否答非所问、内容残缺
    3. 逻辑是否矛盾、有无漏洞
    4. 格式是否规范、是否需要优化

    请输出：问题清单 + 优化方案
    """
    return llm_call(reflect_prompt)

# 3. 第三轮：迭代优化最终结果
def agent_optimize(user_input, raw_result, reflect_report):
    optimize_prompt = f"""
    根据自查纠错报告，优化你的输出，交付最终成品：
    用户需求：{user_input}
    原始结果：{raw_result}
    纠错报告：{reflect_report}

    请修正所有问题，输出精准、完整、高质量的最终结果。
    """
    return llm_call(optimize_prompt)

# ========== 完整纠错Agent主流程 ==========
def final_agent_run(user_task):
    # 初次执行
    raw = agent_execute(user_task)
    # 自我反思
    reflect = agent_reflect(user_task, raw)
    # 迭代优化
    final_result = agent_optimize(user_task, raw, reflect)
    return final_result
