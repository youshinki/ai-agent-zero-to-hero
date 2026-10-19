#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第17篇配套完整项目代码 · tools/tool_manager.py
工具管理器：注册工具 / 生成工具描述 / 执行工具调用
==========================================================================

设计要点（文章第三章）：
  1. 工具注册表        —— 统一管理
  2. 工具描述生成器    —— 转成大模型能理解的格式
  3. 工具执行模块      —— 真实执行函数
==========================================================================
"""

import ast
import json
import os
from typing import Any, Callable, Dict

from config import TOOL_WORKSPACE, MAX_EXPR_LEN


# ======================================================================
# 工具管理器
# ======================================================================

class ToolManager:
    """统一工具注册与执行"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(self, name: str, description: str,
                      parameters: Dict[str, Any], func: Callable):
        """注册一个可用工具"""
        self.tools[name] = {
            "description": description,
            "parameters": parameters,
            "func": func,
        }
    
    def get_tools_description(self) -> str:
        """生成给大模型看的工具描述"""
        desc = "你可以使用以下工具：\n\n"
        for name, tool in self.tools.items():
            desc += f"工具名称：{name}\n"
            desc += f"工具功能：{tool['description']}\n"
            desc += f"输入参数：{json.dumps(tool['parameters'], ensure_ascii=False)}\n"
            desc += "-" * 30 + "\n"
        return desc
    
    def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """真实执行工具调用"""
        if tool_name not in self.tools:
            return f"错误：未找到工具 {tool_name}"
        try:
            # 参数校验：只传该工具声明过的参数
            allowed = set(self.tools[tool_name]["parameters"].keys())
            safe_args = {k: v for k, v in (tool_args or {}).items() if k in allowed}
            result = self.tools[tool_name]["func"](**safe_args)
            return str(result)
        except Exception as e:
            return f"工具执行失败：{e}"


# ======================================================================
# 三个基础工具
# ======================================================================

def _resolve_path(path: str) -> str:
    """路径安全校验：限制在 TOOL_WORKSPACE 内，防止路径穿越"""
    base = os.path.abspath(TOOL_WORKSPACE)
    target = os.path.abspath(os.path.join(base, path))
    if not target.startswith(base + os.sep) and target != base:
        raise ValueError("路径越界：只允许访问工作目录内文件")
    return target


def read_file(path: str) -> str:
    """读取本地文件内容"""
    try:
        real = _resolve_path(path)
        with open(real, "r", encoding="utf-8") as f:
            content = f.read()
        return f"文件内容（{len(content)}字）：\n{content[:3000]}"
    except Exception as e:
        return f"读取文件失败：{e}"


def write_file(path: str, content: str) -> str:
    """写入内容到本地文件"""
    try:
        real = _resolve_path(path)
        os.makedirs(os.path.dirname(real), exist_ok=True) if os.path.dirname(real) else None
        with open(real, "w", encoding="utf-8") as f:
            f.write(content)
        return f"文件写入成功：{path}（{len(content)}字）"
    except Exception as e:
        return f"写入文件失败：{e}"


_ALLOWED_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv)


def _safe_eval(node):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, _ALLOWED_OPS):
        a, b = _safe_eval(node.left), _safe_eval(node.right)
        import operator
        table = {ast.Add: operator.add, ast.Sub: operator.sub,
                 ast.Mult: operator.mul, ast.Div: operator.truediv,
                 ast.Mod: operator.mod, ast.Pow: operator.pow,
                 ast.FloorDiv: operator.floordiv}
        return table[type(node.op)](a, b)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        v = _safe_eval(node.operand)
        return v if isinstance(node.op, ast.UAdd) else -v
    raise ValueError("不支持的表达式")


def calculator(expression: str) -> str:
    """计算数学表达式（AST白名单，安全）"""
    try:
        if len(expression) > MAX_EXPR_LEN:
            return "计算失败：表达式过长"
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算失败：{e}"


def create_default_tools() -> ToolManager:
    """创建默认工具集"""
    tm = ToolManager()
    tm.register_tool(
        name="read_file",
        description="读取本地文件内容，适合获取文档、代码、日志等信息",
        parameters={"path": "文件路径，字符串类型"},
        func=read_file,
    )
    tm.register_tool(
        name="write_file",
        description="将内容写入本地文件，适合保存结果、生成报告、记录数据",
        parameters={
            "path": "文件路径，字符串类型",
            "content": "要写入的内容，字符串类型",
        },
        func=write_file,
    )
    tm.register_tool(
        name="calculator",
        description="计算数学表达式，支持加减乘除和括号",
        parameters={
            "expression": "数学表达式，字符串类型，例如 '12+34'、'(100-20)*5'",
        },
        func=calculator,
    )
    return tm
