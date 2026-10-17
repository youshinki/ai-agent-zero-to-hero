# -*- coding: utf-8 -*-
# 自包含示例：strip_code_block + robust_json_parse（带 response_format 与重试修复）
import os
import json
from openai import OpenAI

# TODO: 请通过环境变量注入密钥
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def strip_code_block(raw_text: str) -> str:
    """第二层：清洗代码块和多余文字"""
    import re
    text = re.sub(r"```(?:json)?\s*", "", raw_text)
    text = re.sub(r"\s*```", "", text)
    start, end = text.find("{"), text.rfind("}")
    return text[start:end + 1].strip() if start != -1 and end > start else text


def robust_json_parse(user_query: str, max_retry: int = 3) -> dict:
    # 第一层：response_format 强制 JSON 模式
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_query}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    cleaned = strip_code_block(resp.choices[0].message.content)

    # 第三层：解析失败则回喂模型自我修复
    for _ in range(max_retry):
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            repair = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user",
                           "content": f"以下JSON有语法错误，只输出修复后的合法JSON：\n{cleaned}"}],
                response_format={"type": "json_object"},
            )
            cleaned = strip_code_block(repair.choices[0].message.content)
    raise ValueError("JSON解析失败，已达最大重试次数")
