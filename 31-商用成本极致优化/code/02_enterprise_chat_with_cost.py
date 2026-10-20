# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 agent_cost_engine/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

"""
带成本优化的企业问答主流程：先导入成本优化器，再在 EnterpriseRAGSystem 中替换 chat 方法。
"""

from commercial.cost_optimizer import cost_opt

def chat(self, user_input: str) -> str:
    # 1. 拦截无效闲聊，直接节流，零消耗
    if cost_opt.is_useless_query(user_input):
        return "您好，我是企业智能知识库助手，请您提问具体业务、资料、流程相关问题，我将为您精准解答。"

    # 2. 优先读取本地缓存，重复问题零API调用
    cache_ans = cost_opt.check_cache(user_input)
    if cache_ans:
        return cache_ans

    # 3. 隐私安全拦截
    safe_check = privacy_safe.forbid_external_leak(user_input)
    if not safe_check:
        return "抱歉，无法提供相关查询内容，仅支持业务资料问答。"

    # 4. 获取知识库检索结果，判断是否需要强模型
    from knowledge_base.kb_core import kb
    kb_result = kb.search(user_input)
    has_content = bool(kb_result and "未检索到" not in kb_result)

    # 5. 智能模型分配（核心省钱）
    model_level = cost_opt.smart_model_route(user_input, has_content)

    # 6. 正常商业化应答
    raw_answer = commercial_agent.safe_answer(user_input)
    final_answer = privacy_safe.safe_reply_filter(user_input, raw_answer)

    # 7. 写入缓存，下次直接复用
    cost_opt.set_cache(user_input, final_answer)

    return final_answer
