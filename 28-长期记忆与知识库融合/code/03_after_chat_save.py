"""
对话结束后自动把问答沉淀进长期记忆。
"""

# 问答结束后自动沉淀记忆
def after_chat_save(user_msg: str, bot_msg: str):
    memory.add_chat_memory(user_msg, bot_msg)
    # 可手动更新用户偏好，例如：
    # memory.update_user_profile("回答风格", "简洁专业")
    # memory.update_user_profile("常用场景", "办公技术问答")
