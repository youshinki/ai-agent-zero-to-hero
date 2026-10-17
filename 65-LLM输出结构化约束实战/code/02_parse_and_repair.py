# -*- coding: utf-8 -*-
# 第二/三层：解析前清洗 + 失败后回喂模型自我修复（最多 2 次）
import os
import json
import re
from openai import OpenAI

# TODO: 请通过环境变量注入密钥
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def safe_parse_json(text):
    # 1. 剥离 ```json ... ``` 代码块
    text = re.sub(r"^```(json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())
    # 2. 截取第一个 { 到最后一个 } 之间的内容，甩掉前后废话
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def parse_with_repair(raw_text, max_retry=2):
    for _ in range(max_retry):
        parsed = safe_parse_json(raw_text)
        if parsed is not None:
            return parsed
        # 没解析出来，把错误回喂让模型修
        raw_text = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content":
                       f"下面不是合法JSON，请修正为严格可解析的JSON，不要加任何解释：\n{raw_text}"}],
        ).choices[0].message.content
    return None   # 真修不好，走兜底


def structured_extract(query):
    raw = call_llm(query)               # 1. 模型输出（占位）
    data = parse_with_repair(raw)        # 2. 清洗+修复
    if data is None or "intent" not in data:
        log_failure(query, raw)          # noqa: F821 留痕
        return {"intent": "other",
                "reply": "抱歉，我没太理解，您可以换个说法或转人工"}
    return data


def call_llm(query):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
    ).choices[0].message.content
