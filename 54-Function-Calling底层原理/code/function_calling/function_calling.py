#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第54篇配套完整项目代码 · function_calling.py
Function Calling 底层原理：模型决策 + 代码执行 的完整闭环

  1. 工具 Schema（JSON Schema）
  2. 模型决策（模拟 tool_calls）
  3. 参数解析与校验
  4. 工具执行与结果回填
  5. 多工具调用与错误处理
==========================================================================
"""

import json
from typing import (Dict, List)


# ======================================================================
# 一、工具 Schema
# ======================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询城市天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名"},
                    "unit": {"type": "string", "enum": ["c", "f"],
                             "description": "温度单位"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"},
                },
                "required": ["expression"],
            },
        },
    },
]


# ======================================================================
# 二、Schema 校验
# ======================================================================

class SchemaValidator:
    @staticmethod
    def validate(tool_name: str, args: Dict) -> Dict:
        schema = next((t["function"] for t in TOOLS
                       if t["function"]["name"] == tool_name), None)
        if not schema:
            return {"valid": False, "error": f"未知工具：{tool_name}"}
        
        params = schema["parameters"]
        required = params.get("required", [])
        props = params.get("properties", {})
        
        # 必填
        for r in required:
            if r not in args:
                return {"valid": False, "error": f"缺少必填参数：{r}"}
        # 类型
        type_map = {"string": str, "number": (int, float), "integer": int,
                    "boolean": bool, "object": dict, "array": list}
        for k, v in args.items():
            if k not in props:
                continue
            expected = props[k].get("type")
            if expected and not isinstance(v, type_map.get(expected, object)):
                return {"valid": False, "error": f"参数 {k} 类型错误"}
            enum = props[k].get("enum")
            if enum and v not in enum:
                return {"valid": False, "error": f"参数 {k} 不在允许值内"}
        return {"valid": True, "args": args}


# ======================================================================
# 三、工具实现
# ======================================================================

class ToolRuntime:
    @staticmethod
    def get_weather(city: str, unit: str = "c") -> str:
        data = {"北京": 22, "上海": 26, "深圳": 28}
        temp = data.get(city)
        if temp is None:
            return f"未找到城市：{city}"
        if unit == "f":
            temp = round(temp * 9 / 5 + 32)
        return f"{city}今天{temp}°{'F' if unit == 'f' else 'C'}，晴"
    
    @staticmethod
    def calculator(expression: str) -> str:
        import re
        if not re.fullmatch(r"[\d\.\+\-\*/\(\)\s]+", expression):
            return "计算失败：表达式非法"
        try:
            return f"{expression} = {eval(expression)}"
        except Exception as e:
            return f"计算失败：{e}"


# ======================================================================
# 四、模型决策（模拟）
# ======================================================================

class MockModel:
    @staticmethod
    def decide(question: str) -> List[Dict]:
        """返回 tool_calls 列表；空列表表示无需工具"""
        import re
        text = question.lower()
        
        if "天气" in question:
            city = next((c for c in ["北京", "上海", "深圳"] if c in question), "北京")
            unit = "f" if ("华氏" in question or "f" in text) else "c"
            return [{"name": "get_weather",
                     "arguments": json.dumps({"city": city, "unit": unit})}]
        
        m = re.search(r"[\d\.\+\-\*/\(\)\s]{3,}", question)
        if m and re.search(r"\d", m.group()):
            return [{"name": "calculator",
                     "arguments": json.dumps({"expression": m.group().strip()})}]
        
        return []


# ======================================================================
# 五、执行闭环
# ======================================================================

class FunctionCallAgent:
    def __init__(self):
        self.runtime = ToolRuntime()
        self.validator = SchemaValidator()
        self.log: List[Dict] = []
    
    def run(self, question: str) -> Dict:
        calls = MockModel.decide(question)
        if not calls:
            return {"question": question, "tools_used": [],
                    "answer": f"关于「{question}」，无需工具，直接回答。",
                    "errors": []}
        
        results, errors = [], []
        for call in calls:
            name = call["name"]
            try:
                args = json.loads(call["arguments"])
            except json.JSONDecodeError:
                errors.append(f"{name}：参数JSON解析失败")
                results.append(f"[{name}] 参数解析失败")
                continue
            
            check = self.validator.validate(name, args)
            if not check["valid"]:
                errors.append(f"{name}：{check['error']}")
                results.append(f"[{name}] {check['error']}")
                continue
            
            fn = getattr(self.runtime, name, None)
            if not fn:
                errors.append(f"{name}：未实现")
                results.append(f"[{name}] 未实现")
                continue
            
            results.append(fn(**check["args"]))
            self.log.append({"tool": name, "args": args, "result": results[-1]})
        
        return {"question": question,
                "tools_used": [c["name"] for c in calls],
                "results": results, "errors": errors,
                "answer": "根据工具结果：" + "；".join(results)}


def demo():
    print("=" * 66)
    print("🔌 Function Calling 底层原理演示")
    print("=" * 66)
    agent = FunctionCallAgent()
    for q in ["北京天气怎么样", "上海华氏温度", "计算 (128+64)*3", "你好"]:
        r = agent.run(q)
        print(f"\n问：{q}")
        print(f"调用工具：{r['tools_used']}")
        print(f"结果：{r.get('results')}")
        print(f"答案：{r['answer']}")
    print(f"\n调用日志：{agent.log}")


if __name__ == "__main__":
    demo()
