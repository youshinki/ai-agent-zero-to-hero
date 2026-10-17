# -*- coding: utf-8 -*-
# Function Calling：parameters 本身就是一份 JSON Schema
import os
import json
from openai import OpenAI

# TODO: 请通过环境变量注入密钥
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 定义工具 —— parameters 本身就是一份 JSON Schema
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市的天气",
        "parameters": {                    # ← 这就是 JSON Schema
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名，如：北京"},
                "unit": {"type": "string",
                         "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["city"],
        },
    },
}]

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
    tools=tools,
    tool_choice="auto",   # 让模型自己决定调不调、传什么参数
)

# 模型严格按 Schema 输出函数调用，参数一定是合法 JSON
call = resp.choices[0].message.tool_calls[0]
args = json.loads(call.function.arguments)
print(call.function.name)  # get_weather
print(args)                 # {'city': '北京', 'unit': 'celsius'}
