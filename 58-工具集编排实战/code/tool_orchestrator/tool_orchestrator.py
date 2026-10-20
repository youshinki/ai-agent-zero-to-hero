#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第58篇配套完整项目代码 · tool_orchestrator.py
工具集编排实战：多工具选择、参数校验、冲突与权限

  1. 工具注册表（能力/权限/优先级）
  2. 工具选择（按任务/权限/冲突）
  3. 参数校验
  4. 冲突消解（重复/互斥）
  5. 编排执行（串行/并行模拟）
==========================================================================
"""

from typing import (Dict, List, Optional)


# ======================================================================
# 一、工具定义
# ======================================================================

class Tool:
    def __init__(self, name: str, description: str, params: List[str],
                 required: List[str], permission: str = "user",
                 priority: int = 1, conflicts: List[str] = None):
        self.name = name
        self.description = description
        self.params = params
        self.required = required
        self.permission = permission
        self.priority = priority
        self.conflicts = conflicts or []
    
    def validate(self, args: Dict) -> Dict:
        for r in self.required:
            if r not in args or args[r] in (None, ""):
                return {"valid": False, "error": f"缺少必填参数：{r}"}
        for k in args:
            if k not in self.params:
                return {"valid": False, "error": f"未知参数：{k}"}
        return {"valid": True}


# ======================================================================
# 二、注册表
# ======================================================================

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        self.tools[tool.name] = tool
    
    def available(self, user_role: str = "user") -> List[Tool]:
        levels = {"user": 0, "admin": 1}
        return [t for t in self.tools.values()
                if levels.get(t.permission, 0) <= levels.get(user_role, 0)]
    
    def get(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)


# ======================================================================
# 三、选择与冲突
# ======================================================================

class ToolSelector:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    def select(self, task: str, user_role: str = "user") -> List[Tool]:
        """按关键词匹配 + 权限过滤 + 优先级排序"""
        candidates = []
        for tool in self.registry.available(user_role):
            if tool.name in task or any(p in task for p in tool.params):
                candidates.append(tool)
            elif tool.description[:2] in task:
                candidates.append(tool)
        
        # 按优先级降序
        candidates.sort(key=lambda t: t.priority, reverse=True)
        return candidates
    
    @staticmethod
    def resolve_conflicts(tools: List[Tool]) -> List[Tool]:
        """移除冲突（互斥）工具：保留优先级高的"""
        kept: List[Tool] = []
        blocked = set()
        for t in tools:
            if t.name in blocked:
                continue
            kept.append(t)
            blocked.update(t.conflicts)
        return kept


# ======================================================================
# 四、运行时
# ======================================================================

class ToolRuntime:
    @staticmethod
    def run(tool: Tool, args: Dict) -> str:
        if tool.name == "read_file":
            return f"已读取文件：{args.get('path')}"
        if tool.name == "write_file":
            return f"已写入文件：{args.get('path')}（{len(args.get('content',''))}字）"
        if tool.name == "delete_file":
            return f"已删除文件：{args.get('path')}"
        if tool.name == "calculator":
            import re
            expr = args.get("expression", "")
            if not re.fullmatch(r"[\d\.\+\-\*/\(\)\s]+", expr):
                return "计算失败：表达式非法"
            return f"{expr} = {eval(expr)}"
        if tool.name == "search":
            return f"搜索：{args.get('query')}（命中3条）"
        return f"[{tool.name}] 已执行"


# ======================================================================
# 五、编排器
# ======================================================================

class Orchestrator:
    def __init__(self):
        self.registry = ToolRegistry()
        self._setup()
        self.selector = ToolSelector(self.registry)
        self.log: List[Dict] = []
    
    def _setup(self):
        self.registry.register(Tool(
            "read_file", "读取文件", ["path"], ["path"], "user", 3))
        self.registry.register(Tool(
            "write_file", "写入文件", ["path", "content"], ["path", "content"],
            "user", 2))
        self.registry.register(Tool(
            "delete_file", "删除文件", ["path"], ["path"], "admin", 1,
            conflicts=["write_file"]))
        self.registry.register(Tool(
            "calculator", "数学计算", ["expression"], ["expression"], "user", 2))
        self.registry.register(Tool(
            "search", "搜索信息", ["query"], ["query"], "user", 2))
    
    def execute(self, task: str, calls: List[Dict],
                user_role: str = "user") -> Dict:
        selected = self.selector.select(task, user_role)
        selected = self.selector.resolve_conflicts(selected)
        selected_names = [t.name for t in selected]
        
        results, errors = [], []
        for call in calls:
            name = call.get("name")
            tool = self.registry.get(name)
            if not tool:
                errors.append(f"未知工具：{name}")
                continue
            if tool.name not in selected_names and name not in self.registry.tools:
                errors.append(f"工具不可用：{name}")
                continue
            # 权限
            if user_role == "user" and tool.permission == "admin":
                errors.append(f"权限不足：{name}（需要管理员）")
                continue
            # 冲突
            if any(c.name in selected_names for c in
                   [self.registry.get(x) for x in tool.conflicts if self.registry.get(x)]):
                pass  # 冲突已在选择阶段处理
            
            check = tool.validate(call.get("args", {}))
            if not check["valid"]:
                errors.append(f"{name}：{check['error']}")
                continue
            
            output = ToolRuntime.run(tool, call["args"])
            results.append({"tool": name, "output": output})
            self.log.append({"tool": name, "args": call["args"]})
        
        return {"task": task, "selected": selected_names,
                "results": results, "errors": errors}


def demo():
    print("=" * 66)
    print("🧰 工具集编排实战演示")
    print("=" * 66)
    orch = Orchestrator()
    
    print("\n[1] 工具选择（普通用户）：")
    for task in ["读取文件 report.txt", "计算 1+2", "搜索资料"]:
        sel = orch.selector.select(task, "user")
        print(f"   {task} → {[t.name for t in sel]}")
    
    print("\n[2] 权限过滤：")
    sel_user = orch.selector.select("删除文件", "user")
    sel_admin = orch.selector.select("删除文件", "admin")
    print(f"   普通用户：{[t.name for t in sel_user]}")
    print(f"   管理员：{[t.name for t in sel_admin]}")
    
    print("\n[3] 冲突消解：")
    tools = [orch.registry.get("delete_file"), orch.registry.get("write_file")]
    kept = orch.selector.resolve_conflicts(tools)
    print(f"   delete_file + write_file → {[t.name for t in kept]}")
    
    print("\n[4] 编排执行：")
    r = orch.execute("读取并计算", [
        {"name": "read_file", "args": {"path": "report.txt"}},
        {"name": "calculator", "args": {"expression": "(128+64)*3"}},
        {"name": "write_file", "args": {"path": "out.txt", "content": "结果"}},
        {"name": "read_file", "args": {}},  # 缺参数
    ])
    for item in r["results"]:
        print(f"   ✅ [{item['tool']}] {item['output']}")
    for e in r["errors"]:
        print(f"   ❌ {e}")
    
    print("\n[5] 权限拦截：")
    r = orch.execute("删除文件", [
        {"name": "delete_file", "args": {"path": "secret.txt"}},
    ], user_role="user")
    print(f"   结果：{r['errors']}")


if __name__ == "__main__":
    demo()
