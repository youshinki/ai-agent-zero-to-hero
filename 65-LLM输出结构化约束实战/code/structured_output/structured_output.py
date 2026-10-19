#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第65篇配套完整项目代码 · structured_output.py
LLM 输出结构化约束：JSON Schema、语法容错、修复与解析兜底

  1. JSON Schema 约束（Prompt + 校验）
  2. 鲁棒解析（提取 JSON / 容错）
  3. 自动修复（尾逗号/单引号/截断）
  4. Schema 校验与字段补全
  5. 解析兜底与重试
==========================================================================
"""

import json
import re
from typing import Any, Dict, List, Optional


# ======================================================================
# 一、Schema
# ======================================================================

ANSWER_SCHEMA = {
    "type": "object",
    "required": ["intent", "confidence"],
    "properties": {
        "intent": {"type": "string",
                   "enum": ["售前", "售后", "其他"]},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "entities": {"type": "array", "items": {"type": "string"}},
    },
}


# ======================================================================
# 二、鲁棒解析
# ======================================================================

def extract_json(text: str) -> Optional[str]:
    """从混合文本中提取第一个完整 JSON 对象"""
    # 去除 markdown 代码块
    text = re.sub(r"```(?:json)?", "", text).replace("```", "")
    start = text.find("{")
    if start == -1:
        return None
    depth, in_str, escape = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    return text[start:]  # 截断（未闭合）


def repair_json(raw: str) -> str:
    """常见语法修复"""
    s = raw.strip()
    s = s.replace("'", '"')                      # 单引号 → 双引号
    s = re.sub(r",\s*([}\]])", r"\1", s)         # 尾逗号
    s = re.sub(r"(\w+)\s*:", r'"\1":', s)        # 裸键名
    s = re.sub(r":\s*'([^']*)'", r': "\1"', s)
    return s


def parse_robust(text: str) -> Dict:
    """多级兜底解析"""
    if not text:
        return {"ok": False, "error": "空输出"}
    
    candidate = extract_json(text)
    if candidate is None:
        return {"ok": False, "error": "未找到JSON"}
    
    # 1. 直接解析
    try:
        return {"ok": True, "data": json.loads(candidate), "repaired": False}
    except json.JSONDecodeError:
        pass
    
    # 2. 修复后解析
    try:
        fixed = repair_json(candidate)
        return {"ok": True, "data": json.loads(fixed), "repaired": True}
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"解析失败：{e}", "raw": candidate[:100]}


# ======================================================================
# 三、Schema 校验
# ======================================================================

class SchemaValidator:
    @staticmethod
    def validate(data: Any, schema: Dict) -> Dict:
        errors = []
        
        if schema.get("type") == "object":
            if not isinstance(data, dict):
                return {"valid": False, "errors": ["应为对象"]}
            for req in schema.get("required", []):
                if req not in data:
                    errors.append(f"缺少字段：{req}")
            for key, sub in schema.get("properties", {}).items():
                if key in data:
                    errors.extend(SchemaValidator._check(data[key], sub, key))
        
        return {"valid": not errors, "errors": errors}
    
    @staticmethod
    def _check(value, schema: Dict, path: str) -> List[str]:
        errors = []
        t = schema.get("type")
        type_map = {"string": str, "number": (int, float),
                    "integer": int, "boolean": bool,
                    "array": list, "object": dict}
        if t and not isinstance(value, type_map.get(t, object)):
            return [f"{path} 类型错误（期望{t}）"]
        if t == "number":
            if "minimum" in schema and value < schema["minimum"]:
                errors.append(f"{path} 小于最小值")
            if "maximum" in schema and value > schema["maximum"]:
                errors.append(f"{path} 大于最大值")
        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"{path} 不在枚举内")
        if t == "array" and "items" in schema:
            for i, item in enumerate(value):
                errors.extend(SchemaValidator._check(item, schema["items"], f"{path}[{i}]"))
        return errors


# ======================================================================
# 四、约束生成
# ======================================================================

def build_constrained_prompt(task: str, schema: Dict) -> str:
    return (f"请完成以下任务并以 JSON 输出，必须符合给定 Schema。\n"
            f"任务：{task}\n"
            f"Schema：{json.dumps(schema, ensure_ascii=False)}\n"
            f"只输出 JSON，不要任何解释。")


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("📐 LLM 输出结构化约束演示")
    print("=" * 66)
    
    cases = {
        "标准JSON": '{"intent": "售前", "confidence": 0.9}',
        "带markdown": '```json\n{"intent": "售后", "confidence": 0.8}\n```',
        "单引号+尾逗号": "{'intent': '其他', 'confidence': 0.5,}",
        "裸键名": "{intent: 售前, confidence: 0.7}",
        "混合文本": "分析结果如下：{\"intent\": \"售前\", \"confidence\": 0.85} 请查收",
        "截断JSON": '{"intent": "售前", "confidence": 0.',
        "无JSON": "抱歉我不知道",
    }
    for name, text in cases.items():
        r = parse_robust(text)
        print(f"\n[{name}]")
        if r["ok"]:
            v = SchemaValidator.validate(r["data"], ANSWER_SCHEMA)
            print(f"   解析：✅（修复={r.get('repaired')}）")
            print(f"   数据：{r['data']}")
            print(f"   校验：{'✅ 通过' if v['valid'] else '❌ ' + str(v['errors'])}")
        else:
            print(f"   解析：❌ {r['error']}")
    
    print("\n[Prompt 约束示例]")
    print(build_constrained_prompt("判断用户意图", ANSWER_SCHEMA))


if __name__ == "__main__":
    demo()
