#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第52篇配套完整项目代码 · agent_architecture.py
Agent 核心架构总览：从 LLM 到自主决策完整链路

  组件：LLM / 感知 / 规划 / 记忆 / 工具 / 反思 / 执行
  链路：感知 → 记忆 → 规划 → 工具 → 执行 → 反思 → 沉淀
  范式：ReAct / Plan-and-Execute / Reflexion / Multi-Agent
==========================================================================
"""

from typing import Dict, List


# ======================================================================
# 一、七大组件
# ======================================================================

class LLM:
    def __init__(self, model="mock-llm"):
        self.model = model
    
    def think(self, prompt: str) -> str:
        return f"[{self.model}] 思考：{prompt[:40]}"


class Perception:
    def parse(self, raw: str) -> Dict:
        intent = "question"
        if any(k in raw for k in ["帮我", "生成", "整理", "分析"]):
            intent = "task"
        return {"raw": raw, "intent": intent, "entities": raw.split()[:3]}


class Planner:
    def plan(self, goal: str) -> List[str]:
        return [f"理解目标：{goal}", "收集信息", "执行任务", "检查质量", "输出结果"]


class MemoryModule:
    def __init__(self):
        self.short: List[str] = []
        self.long: List[str] = []
    
    def remember(self, item: str, long_term: bool = False):
        (self.long if long_term else self.short).append(item)
        if len(self.short) > 20:
            self.short = self.short[-10:]
    
    def recall(self, query: str) -> List[str]:
        return [x for x in self.short + self.long if query in x][:3]


class ToolModule:
    def __init__(self):
        self.tools = {
            "search": lambda q: f"搜索结果：{q}",
            "calc": self._calc,
            "read": lambda p: f"文件内容：{p}",
        }
    
    @staticmethod
    def _calc(expr: str) -> str:
        import re
        if not re.fullmatch(r"[\d\.\+\-\*/\(\)\s]+", expr):
            return "计算结果：N/A"
        try:
            return f"计算结果：{eval(expr)}"
        except Exception:
            return "计算结果：N/A"
    
    def call(self, name: str, arg: str) -> str:
        fn = self.tools.get(name)
        return fn(arg) if fn else f"未知工具：{name}"


class Reflection:
    def check(self, result: str) -> List[str]:
        issues = []
        if len(result) < 10:
            issues.append("内容过短")
        if "错误" in result:
            issues.append("包含错误信息")
        return issues


class Executor:
    def run(self, plan: List[str], tools: ToolModule) -> List[str]:
        outputs = []
        for step in plan:
            if "收集" in step:
                outputs.append(tools.call("search", step))
            else:
                outputs.append(f"执行：{step}")
        return outputs


# ======================================================================
# 二、完整 Agent
# ======================================================================

class Agent:
    def __init__(self):
        self.llm = LLM()
        self.perception = Perception()
        self.planner = Planner()
        self.memory = MemoryModule()
        self.tools = ToolModule()
        self.reflection = Reflection()
        self.executor = Executor()
    
    def run(self, user_input: str) -> Dict:
        trace = []
        # 1. 感知
        parsed = self.perception.parse(user_input)
        trace.append(("感知", parsed["intent"]))
        # 2. 记忆
        recalled = self.memory.recall(user_input)
        trace.append(("记忆", f"召回{len(recalled)}条"))
        # 3. 规划
        plan = self.planner.plan(parsed["raw"])
        trace.append(("规划", f"{len(plan)}步"))
        # 4. 工具 + 5. 执行
        outputs = self.executor.run(plan, self.tools)
        trace.append(("执行", f"{len(outputs)}个输出"))
        # 6. 反思
        issues = self.reflection.check("\n".join(outputs))
        trace.append(("反思", f"{len(issues)}个问题"))
        # 7. 沉淀
        self.memory.remember(parsed["raw"], long_term=True)
        trace.append(("沉淀", "已写入长期记忆"))
        
        return {"input": user_input, "plan": plan, "outputs": outputs,
                "issues": issues, "trace": trace}


# ======================================================================
# 三、四种范式
# ======================================================================

PATTERNS = {
    "ReAct": {"loop": "思考→行动→观察", "use": "工具调用/信息搜索", "复杂": "中"},
    "Plan-and-Execute": {"loop": "先规划→逐步执行", "use": "长周期复杂任务", "复杂": "高"},
    "Reflexion": {"loop": "执行→反思→改进", "use": "高质量输出", "复杂": "高"},
    "Multi-Agent": {"loop": "分工→协作→仲裁", "use": "复杂系统", "复杂": "很高"},
}


def demo():
    print("=" * 66)
    print("🤖 Agent 核心架构总览演示")
    print("=" * 66)
    agent = Agent()
    r = agent.run("帮我分析AI Agent趋势并生成报告")
    print(f"\n输入：{r['input']}")
    print(f"\n执行链路：")
    for stage, info in r["trace"]:
        print(f"  {stage}：{info}")
    print(f"\n计划：")
    for i, p in enumerate(r["plan"], 1):
        print(f"  {i}. {p}")
    print(f"\n输出：{r['outputs'][:2]}")
    print(f"\n范式对比：")
    for name, info in PATTERNS.items():
        print(f"  {name}：{info['loop']}（{info['use']}，复杂度{info['复杂']}）")


if __name__ == "__main__":
    demo()
