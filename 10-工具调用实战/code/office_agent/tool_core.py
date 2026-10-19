#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第10篇配套完整项目代码 · tool_core.py
工具注册与执行模块（Function Call 的"执行端"）

三个实用办公工具（文章第四章）：
  1. get_current_time  - 获取当前系统时间
  2. read_file_content - 读取本地文本文件
  3. calculate         - 执行数学计算
==========================================================================
"""

import ast
import datetime
import os
from typing import Any, Dict

from config import SAFE_EVAL_MAX_LENGTH


# ======================================================================
# 一、工具定义（告诉模型有哪些工具可用）—— Function Call 要素1
# ======================================================================

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前系统日期和时间，当用户问现在几点、今天几号时使用",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_content",
            "description": "读取本地文本文件的内容，当用户要求查看、读取、分析某个文件时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要读取的文件路径，例如 ./docs/report.txt"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学表达式计算，当用户需要精确数值计算时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，例如 123.5 * 0.85 + 200"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# 工具名 → 描述（便于打印与调试）
TOOL_NAMES = [t["function"]["name"] for t in TOOLS_DEFINITION]


# ======================================================================
# 二、安全计算器（受限 AST 求值，不执行任意代码）
# ======================================================================

_ALLOWED_BIN_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
                    ast.FloorDiv)
_ALLOWED_UNARY_OPS = (ast.UAdd, ast.USub)
_ALLOWED_FUNCS = {
    "abs": abs, "round": round, "min": min, "max": max,
    "sum": sum, "pow": pow, "int": int, "float": float,
}


def safe_calculate(expression: str) -> float:
    """安全的数学表达式求值（AST白名单，禁止任意代码执行）"""
    if len(expression) > SAFE_EVAL_MAX_LENGTH:
        raise ValueError("表达式过长")
    
    tree = ast.parse(expression, mode="eval")
    
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("仅支持数字常量")
        if isinstance(node, ast.BinOp):
            if not isinstance(node.op, _ALLOWED_BIN_OPS):
                raise ValueError("不支持的运算符")
            return _apply_op(node.op, _eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, _ALLOWED_UNARY_OPS):
                raise ValueError("不支持的一元运算符")
            val = _eval(node.operand)
            return +val if isinstance(node.op, ast.UAdd) else -val
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCS:
                raise ValueError("不支持的函数")
            if node.keywords:
                raise ValueError("不支持关键字参数")
            return _ALLOWED_FUNCS[node.func.id](*[_eval(a) for a in node.args])
        if isinstance(node, ast.Name):
            raise ValueError(f"不支持的变量: {node.id}")
        raise ValueError(f"不支持语法: {type(node).__name__}")
    
    return _eval(tree)


def _apply_op(op, a, b):
    import operator
    table = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Mod: operator.mod, ast.Pow: operator.pow,
        ast.FloorDiv: operator.floordiv,
    }
    return table[type(op)](a, b)


# ======================================================================
# 三、工具实际执行函数 —— Function Call 要素3
# ======================================================================

def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> str:
    """根据工具名称和参数，真正执行对应功能
    
    模型只负责"说"要调用什么（要素2），真正执行在这里。
    """
    if tool_name == "get_current_time":
        now = datetime.datetime.now()
        weekday = ["一", "二", "三", "四", "五", "六", "日"][now.weekday()]
        return f"当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')} 星期{weekday}"
    
    if tool_name == "read_file_content":
        file_path = tool_args.get("file_path", "")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return f"文件内容（共{len(content)}字）：\n{content[:2000]}"
        except FileNotFoundError:
            return f"错误：找不到文件 {file_path}"
        except Exception as e:
            return f"读取文件出错：{e}"
    
    if tool_name == "calculate":
        expr = tool_args.get("expression", "")
        try:
            result = safe_calculate(expr)
            return f"计算结果：{expr} = {result}"
        except Exception as e:
            return f"计算出错：{e}"
    
    return f"错误：未知工具 {tool_name}"


def execute_all_tool_calls(tool_calls) -> str:
    """批量执行模型返回的多个工具调用"""
    results = []
    for call in tool_calls:
        name = call.function.name
        try:
            import json
            args = json.loads(call.function.arguments or "{}")
        except Exception:
            args = {}
        print(f"  🛠 调用工具：{name} | 参数：{args}")
        result = execute_tool(name, args)
        results.append(f"【{name}】\n{result}")
    return "\n\n".join(results)
