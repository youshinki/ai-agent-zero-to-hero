#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第53篇配套完整项目代码 · react_agent.py
ReAct 模式深度剖析：Thought → Action → Observation 循环底层实现

  1. Prompt 模板与工具描述
  2. 输出解析器（Thought/Action/Final Answer）
  3. 工具执行与观察回填
  4. 最大步数 / 异常兜底
  5. 多步推理演示
==========================================================================
"""

import re
from typing import (Dict, List)


# ======================================================================
# 一、Prompt 模板
# ======================================================================

REACT_PROMPT = """你是一个智能助手，通过思考和调用工具解决问题。

可用工具：
{tools}

输出格式（每轮）：
Thought: <思考>
Action: <工具名> | <参数>

信息足够时直接：
Final Answer: <答案>

历史：
{history}

问题：{question}
"""


# ======================================================================
# 二、工具
# ======================================================================

class Tools:
    def __init__(self):
        self.registry = {
            "search": ("搜索互联网", self._search),
            "calculator": ("数学计算", self._calc),
            "get_weather": ("查询天气", self._weather),
        }
    
    @staticmethod
    def _search(query: str) -> str:
        return f"搜索结果：关于「{query}」找到 3 条相关信息"
    
    @staticmethod
    def _calc(expr: str) -> str:
        try:
            if not re.fullmatch(r"[\d\.\+\-\*/\(\)\s]+", expr):
                return "计算失败：表达式非法"
            return f"计算结果：{expr} = {eval(expr)}"
        except Exception as e:
            return f"计算失败：{e}"
    
    @staticmethod
    def _weather(city: str) -> str:
        data = {"北京": "晴 22℃", "上海": "多云 26℃", "深圳": "晴 28℃"}
        return f"{city}天气：{data.get(city, '未知')}"
    
    def describe(self) -> str:
        return "\n".join(f"- {n}：{d}" for n, (d, _) in self.registry.items())
    
    def call(self, name: str, arg: str) -> str:
        item = self.registry.get(name)
        if not item:
            return f"错误：未知工具 {name}"
        return item[1](arg)


# ======================================================================
# 三、解析器
# ======================================================================

def parse_output(text: str) -> Dict:
    if "Final Answer:" in text:
        return {"type": "final",
                "content": text.split("Final Answer:", 1)[1].strip()}
    m = re.search(r"Action:\s*(\w+)\s*\|\s*(.+)", text)
    if m:
        return {"type": "action", "tool": m.group(1).strip(),
                "arg": m.group(2).strip()}
    m = re.search(r"Thought:\s*(.+)", text)
    if m:
        return {"type": "thought", "content": m.group(1).strip()}
    return {"type": "unknown", "content": text.strip()}


# ======================================================================
# 四、ReAct Agent
# ======================================================================

class ReActAgent:
    def __init__(self, max_steps: int = 6, verbose: bool = True):
        self.tools = Tools()
        self.max_steps = max_steps
        self.verbose = verbose
        self.history: List[str] = []
    
    def _mock_llm(self, question: str, step: int) -> str:
        """模拟LLM决策（真实模式替换为API调用）"""
        q = question
        if step == 1 and ("天气" in q or "气温" in q):
            city = next((c for c in ["北京", "上海", "深圳"] if c in q), "北京")
            return f"Thought: 需要查询天气。\nAction: get_weather | {city}"
        if step == 1 and ("计算" in q or re.search(r"\d[\+\-\*/]\d", q)):
            expr = re.search(r"[\d\.\+\-\*/\(\)\s]+", q)
            expr = expr.group().strip() if expr else "1+1"
            return f"Thought: 需要计算。\nAction: calculator | {expr}"
        if step == 1 and ("搜索" in q or "资料" in q):
            return f"Thought: 需要搜索资料。\nAction: search | {q[:20]}"
        # 有历史观察则总结
        if self.history:
            last = self.history[-1]
            return f"Thought: 已获取信息。\nFinal Answer: 根据观察：{last}"
        return "Final Answer: 无法判断，请提供更明确的问题。"
    
    def run(self, question: str) -> Dict:
        self.history = []
        steps_log = []
        
        for step in range(1, self.max_steps + 1):
            raw = self._mock_llm(question, step)
            parsed = parse_output(raw)
            
            if self.verbose:
                print(f"  Step{step}: {raw.splitlines()[0][:60]}")
            
            if parsed["type"] == "final":
                steps_log.append({"step": step, "type": "final",
                                  "content": parsed["content"]})
                return {"question": question, "answer": parsed["content"],
                        "steps": steps_log, "ok": True}
            
            if parsed["type"] == "action":
                result = self.tools.call(parsed["tool"], parsed["arg"])
                self.history.append(result)
                steps_log.append({"step": step, "type": "action",
                                  "tool": parsed["tool"], "arg": parsed["arg"],
                                  "observation": result})
                if self.verbose:
                    print(f"    → {result[:60]}")
                continue
            
            # thought 或无行动 → 兜底
            steps_log.append({"step": step, "type": parsed["type"]})
        
        return {"question": question, "answer": "达到最大步数，任务未完成",
                "steps": steps_log, "ok": False}


def demo():
    print("=" * 66)
    print("🔄 ReAct 模式深度剖析演示")
    print("=" * 66)
    agent = ReActAgent()
    for q in ["北京天气怎么样", "计算 (128+64)*3", "搜索AI Agent趋势"]:
        print(f"\n问题：{q}")
        r = agent.run(q)
        print(f"答案：{r['answer']}")
        print(f"步数：{len(r['steps'])}，成功：{r['ok']}")


if __name__ == "__main__":
    demo()
