# -*- coding: utf-8 -*-
# 从模型乱七八糟的输出中抢救出 JSON：去代码块 + 截取大括号 + 容错小毛病
import re
import json


def extract_json(raw_text: str) -> dict:
    """从模型乱七八遭的输出中抢救出JSON"""
    # 1. 去掉 ```json ... ``` 或 ``` ... ``` 包裹
    text = re.sub(r"```(?:json|JSON)?\s*", "", raw_text)
    text = re.sub(r"\s*```", "", text)

    # 2. 截取第一个 { 到最后一个 } 之间的内容
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("未找到JSON对象")
    text = text[start:end + 1]

    # 3. 容错常见小毛病：尾逗号、单引号
    text = re.sub(r",\s*([}\]])", r"\1", text)  # 去掉尾逗号
    text = text.replace("'", '"')  # 单引号转双引号

    return json.loads(text)


# 使用示例
raw = '好的，结果如下：\n```json\n{"result": 42, "status": "ok",\n}\n```\n希望对你有帮助！'
data = extract_json(raw)
print(data)  # {'result': 42, 'status': 'ok'}
