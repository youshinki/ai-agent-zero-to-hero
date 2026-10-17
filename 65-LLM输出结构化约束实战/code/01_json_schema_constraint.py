# -*- coding: utf-8 -*-
# 第一层：用 JSON Schema 在采样层钉死输出结构
import os
from openai import OpenAI

# TODO: 请通过环境变量注入密钥
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": query}],  # noqa: F821
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "order_intent",
            "schema": {
                "type": "object",
                "properties": {
                    "intent": {"type": "string",
                               "enum": ["query_order", "refund", "other"]},
                    "order_id": {"type": "string"},
                },
                "required": ["intent"],
            },
        },
    },
)
