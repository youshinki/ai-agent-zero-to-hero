#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第20篇配套完整项目代码 · tools/tool_manager.py
工具管理器 + 私有知识库工具（文章第七章）
==========================================================================
"""

import ast
import json
import os
from typing import Any, Callable, Dict

from config import TOOL_WORKSPACE, MAX_EXPR_LEN
from knowledge_base.kb_core import kb


class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(self, name: str, description: str,
                      parameters: Dict[str, Any], func: Callable):
        self.tools[name] = {"description": description,
                            "parameters": parameters, "func": func}
    
    def get_tools_description(self) -> str:
        desc = "你可以使用以下工具：\n\n"
        for name, tool in self.tools.items():
            desc += f"工具名称：{name}\n工具功能：{tool['description']}\n"
            desc += f"输入参数：{json.dumps(tool['parameters'], ensure_ascii=False)}\n"
            desc += "-" * 30 + "\n"
        return desc
    
    def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        if tool_name not in self.tools:
            return f"错误：未找到工具 {tool_name}"
        try:
            allowed = set(self.tools[tool_name]["parameters"].keys())
            safe_args = {k: v for k, v in (tool_args or {}).items() if k in allowed}
            return str(self.tools[tool_name]["func"](**safe_args))
        except Exception as e:
            return f"工具执行失败：{e}"


# ---------------- 基础工具 ----------------

def _resolve_path(path: str) -> str:
    base = os.path.abspath(TOOL_WORKSPACE)
    target = os.path.abspath(os.path.join(base, path))
    if not target.startswith(base + os.sep) and target != base:
        raise ValueError("路径越界")
    return target


def read_file(path: str) -> str:
    try:
        real = _resolve_path(path)
        with open(real, "r", encoding="utf-8") as f:
            content = f.read()
        return f"文件内容（{len(content)}字）：\n{content[:3000]}"
    except Exception as e:
        return f"读取文件失败：{e}"


def write_file(path: str, content: str) -> str:
    try:
        real = _resolve_path(path)
        d = os.path.dirname(real)
        if d:
            os.makedirs(d, exist_ok=True)
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
        import operator
        table = {ast.Add: operator.add, ast.Sub: operator.sub,
                 ast.Mult: operator.mul, ast.Div: operator.truediv,
                 ast.Mod: operator.mod, ast.Pow: operator.pow,
                 ast.FloorDiv: operator.floordiv}
        return table[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        v = _safe_eval(node.operand)
        return v if isinstance(node.op, ast.UAdd) else -v
    raise ValueError("不支持的表达式")


def calculator(expression: str) -> str:
    try:
        if len(expression) > MAX_EXPR_LEN:
            return "计算失败：表达式过长"
        return f"计算结果：{expression} = {_safe_eval(ast.parse(expression, mode='eval'))}"
    except Exception as e:
        return f"计算失败：{e}"


# ---------------- 知识库工具（第20篇新增） ----------------

def kb_upload_doc(file_path: str) -> str:
    """上传本地文档到私有知识库"""
    return kb.add_doc_file(file_path)


def kb_search_query(query: str) -> str:
    """基于私有知识库进行语义检索"""
    hits = kb.search(query, top_k=3)
    if not hits:
        return "知识库暂无相关内容"
    def _fmt(h):
        score = h.get("total_score", h.get("score", 0))
        return f"[{h['source']}#{h['chunk_idx']}]（综合分{score}）{h['content']}"
    return "\n\n".join(_fmt(h) for h in hits)


def kb_clear() -> str:
    """清空私有知识库"""
    return kb.clear_kb()


def kb_scan_update() -> str:
    """扫描 upload_doc 目录，全自动增量更新知识库"""
    log = kb.scan_all_update()
    if not log:
        return "目录内暂无可更新文档"
    return "\n".join(f"{item['file']}：{item['message']}" for item in log)


def kb_increment_file(file_path: str) -> str:
    """单文件增量更新（适配新增/修改/删除）"""
    return kb.single_file_increment_update(file_path)["message"]


def kb_cleanup_orphans() -> str:
    """清理已删除文件的残留向量"""
    return kb.cleanup_orphans()


def create_default_tools() -> ToolManager:
    tm = ToolManager()
    tm.register_tool("read_file", "读取本地文件内容", {"path": "文件路径，字符串"}, read_file)
    tm.register_tool("write_file", "将内容写入本地文件",
                     {"path": "文件路径", "content": "要写入的内容"}, write_file)
    tm.register_tool("calculator", "计算数学表达式", {"expression": "数学表达式"}, calculator)
    tm.register_tool("kb_upload_doc", "上传本地文档到私有知识库，支持 pdf/docx/txt/md（切片+向量化入库）",
                     {"file_path": "文档路径，如 knowledge_base/upload_doc/product.txt"}, kb_upload_doc)
    tm.register_tool("kb_search_query", "基于私有知识库语义检索，获取精准私有资料",
                     {"query": "检索关键词或问题"}, kb_search_query)
    tm.register_tool("kb_clear", "清空私有知识库", {}, kb_clear)
    tm.register_tool("kb_scan_update", "扫描目录并全自动增量更新知识库，支持pdf/docx/txt/md（只处理新增/修改文件）", {}, kb_scan_update)
    tm.register_tool("kb_increment_file", "单文件增量更新",
                     {"file_path": "文档路径"}, kb_increment_file)
    tm.register_tool("kb_cleanup_orphans", "清理已删除文件的残留向量", {}, kb_cleanup_orphans)
    return tm
