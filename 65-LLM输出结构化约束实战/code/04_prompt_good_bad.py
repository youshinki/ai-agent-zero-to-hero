# -*- coding: utf-8 -*-
# 对比：差的 Prompt（只靠嘴说）vs 可靠的 Prompt（明确字段 + response_format）

# ❌ 差的 Prompt —— 只靠嘴说，模型经常不遵守
bad_prompt = """
请输出一个用户信息，要求JSON格式。
"""
# 模型可能返回：
# "好的，这是用户信息：\n{\n  \"name\": \"张三\"\n}"
# —— 带解释文字，还可能缺字段，你得自己猜着补

# ✅ 可靠的 Prompt —— 明确字段 + 配合 response_format
good_prompt = """
你是一个信息提取器，只输出JSON对象，禁止输出任何解释文字。
必须包含以下字段：
- name: 姓名（字符串，必填）
- age: 年龄（整数，必填）
- city: 城市（字符串，选填，缺省填"未知"）
从下面的用户输入中提取：
{user_input}
"""
# 调用时加上：response_format={"type": "json_object"}
# 两道保险叠加，不稳定率从 ~15% 降到 <1%
