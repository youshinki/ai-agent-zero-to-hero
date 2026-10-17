# ---- 片段：记忆模块：写入/检索/带记忆回复示例（block 1）----
# 1. 模拟长期记忆库
long_term_memory = []

# 2. 写入记忆
def save_memory(item):
    long_term_memory.append(item)

# 3. 检索记忆
def retrieve_memory(query):
    # 这里简化处理，真实场景使用向量检索
    related = [item for item in long_term_memory if query in item]
    return related

# 4. 生成回复
def generate_reply(user_input):
    memory = retrieve_memory(user_input)

    prompt = f"""
    用户输入：{user_input}
    历史记忆：{memory}
    请参考历史记忆，生成符合用户偏好的回复。
    """

    return call_llm(prompt)

# ---- 片段：记忆模块：写入/检索/带记忆回复示例（block 2）----
# 第一次：写入偏好
save_memory("用户周报喜欢结果先行，突出数据和进度。")

# 第二次：自动参考记忆
result = generate_reply("帮我写本周工作总结。")
