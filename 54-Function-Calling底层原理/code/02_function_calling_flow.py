# -*- coding: utf-8 -*-
# Function Calling 完整调用流程：你 -> 模型 -> 你(执行工具) -> 模型 -> 最终答案
import os
from openai import OpenAI

# TODO: 请通过环境变量注入密钥
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 工具定义（schema 见同目录 01_get_weather_tool.json）
get_weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市的实时天气",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
}


def get_weather(city: str):
    # 实际调用天气 API；这里返回占位结果
    return {"temp": 18, "weather": "晴", "wind": "西北风3级"}


# 第 1 步：你把用户问题 + 工具定义一起发给模型
messages = [{"role": "user", "content": "北京今天天气怎么样？"}]
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=[get_weather_tool],
)

# 第 2 步：模型返回工具调用指令（示例）：
# {
#   "tool_calls": [{
#     "function": {
#       "name": "get_weather",
#       "arguments": "{\"city\": \"北京\"}"
#     }
#   }]
# }

# 第 3 步：你执行工具，拿到结果
result = get_weather("北京")
# -> {"temp": 18, "weather": "晴", "wind": "西北风3级"}

# 第 4 步：把结果喂回给模型
messages.append(response.choices[0].message)
messages.append({
    "role": "tool",
    "tool_call_id": "call_abc123",
    "content": str(result),
})

final_response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=[get_weather_tool],
)

# 第 5 步：模型输出最终答案，例如：
# 北京今天晴，气温 18℃，西北风 3 级，适合出门。
