"""
双引擎融合上下文：先导入依赖，再定义系统提示词与融合函数。
"""

from knowledge_base.kb_core import kb
from knowledge_base.memory_core import memory

def build_fusion_context(user_input: str) -> str:
    """
    构建双引擎融合上下文
    1. 用户偏好档案 2. 近期长期记忆 3. 私有知识库资料
    """
    # 1. 获取用户个人偏好
    profile_ctx = memory.get_user_profile()
    # 2. 获取近期对话记忆
    memory_ctx = memory.get_recent_memory(top_k=6)
    # 3. 获取知识库专业资料
    kb_ctx = kb.search(user_input)

    # 融合所有上下文
    fusion_ctx = "# 用户专属信息与私有知识上下文\n"
    if profile_ctx:
        fusion_ctx += profile_ctx + "\n"
    fusion_ctx += memory_ctx + "\n"
    fusion_ctx += kb_ctx

    return fusion_ctx

FUSION_SYSTEM_PROMPT = """
你是用户的专属私人AI大脑，依托【长期记忆】+【私有知识库】双引擎工作，严格遵守以下规则：
1. 优先结合用户个人偏好、历史对话习惯，输出贴合用户风格的回答；
2. 涉及专业知识、文档资料、事实数据，必须以私有知识库内容为准，带引用溯源；
3. 记忆负责个性化、场景化、习惯适配，知识库负责真实性、专业性、准确性；
4. 禁止编造信息、禁止脱离私有资料、禁止遗忘用户长期设定；
5. 回答自然流畅，贴合用户习惯，同时保证内容精准有据可查。
"""
