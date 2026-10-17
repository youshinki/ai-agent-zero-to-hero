# ===== tools/tool_manager.py：工具管理器 =====

import json
from typing import Callable, Dict, Any

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        func: Callable
    ):
        """注册一个可用工具"""
        self.tools[name] = {
            "description": description,
            "parameters": parameters,
            "func": func
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
            result = self.tools[tool_name]["func"](**tool_args)
            return str(result)
        except Exception as e:
            return f"工具执行失败：{str(e)}"
