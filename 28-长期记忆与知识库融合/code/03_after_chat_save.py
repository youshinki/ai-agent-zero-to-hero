# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 agent_fusion_brain/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

"""
对话结束后自动把问答沉淀进长期记忆。
"""

# 问答结束后自动沉淀记忆
def after_chat_save(user_msg: str, bot_msg: str):
    memory.add_chat_memory(user_msg, bot_msg)
    # 可手动更新用户偏好，例如：
    # memory.update_user_profile("回答风格", "简洁专业")
    # memory.update_user_profile("常用场景", "办公技术问答")
