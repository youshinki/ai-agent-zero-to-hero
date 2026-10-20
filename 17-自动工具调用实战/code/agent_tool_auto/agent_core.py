#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第17篇配套完整项目代码 · agent_core.py
自动工具调用 Agent：
  1. 自主判断是否需要工具
  2. 自主选择工具 + 生成参数
  3. 程序执行真实工具
  4. 根据工具结果继续分析生成最终答案
==========================================================================
"""

import json
import re
import time
from typing import Any, Dict, List

from config import (USE_MOCK, MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL)
from memory_utils import compress_history, build_context
from tools.tool_manager import create_default_tools


tool_manager = create_default_tools()


# ======================================================================
# 模拟决策引擎（真实模式下由大模型输出决策JSON）
# ======================================================================

class MockToolDecider:
    """模拟Agent的工具决策：返回 {tool_call, tool_name, tool_args} 或 {tool_call: False, answer}"""
    
    @staticmethod
    def decide(user_input: str) -> Dict[str, Any]:
        text = user_input.strip()
        
        # 1) 写入任务："把<内容>写入<path>：<要写的内容>"
        m = re.search(r"(?:写入到|保存到|保存至|写入|写到)\s*([^\s，。：:]+)(?:[：:](.+))?", text)
        if m:
            path = m.group(1).strip("，。")
            trailing = (m.group(2) or "").strip()
            # 内容优先级：冒号后文本 > "把<内容>"中的内容 > 任务兜底
            content = trailing
            if not content:
                m2 = re.search(r"把(.+?)(?:写入|保存|写到|保存到|写入到)", text)
                if m2:
                    content = m2.group(1).strip("：:，。 ")
            # 如果包含计算：先算再写
            m_calc = re.search(r"计算\s*([\d\.\s\+\-\*\/\(\)%]+)", text)
            if m_calc:
                expr = m_calc.group(1).strip()
                return {
                    "tool_call": True,
                    "tool_name": "calculator",
                    "tool_args": {"expression": expr},
                    "_next_write": {"path": path, "content_template": "计算结果：{result}"},
                }
            if not content:
                content = f"任务产出：{text}"
            return {"tool_call": True, "tool_name": "write_file",
                    "tool_args": {"path": path, "content": content}}
        
        # 2) 读取任务
        m = re.search(r"(?:读取|查看|打开|读一下|分析)\s*([^\s，。]+\.(?:txt|md|json|csv|py|log))", text)
        if m:
            return {"tool_call": True, "tool_name": "read_file",
                    "tool_args": {"path": m.group(1)}}
        
        # 3) 计算任务
        m = re.search(r"(?:计算|算一下|求)\s*([\d\.\s\+\-\*\/\(\)%]+)", text)
        if m:
            return {"tool_call": True, "tool_name": "calculator",
                    "tool_args": {"expression": m.group(1).strip()}}
        
        # 4) 不需要工具
        return {"tool_call": False, "answer": f"关于「{text}」，这是一个可以直接回答的问题，无需调用外部工具。"}


# ======================================================================
# LLM客户端
# ======================================================================

class LLMClient:
    def __init__(self):
        self.use_mock = USE_MOCK
        self.client = None
        if not self.use_mock:
            from openai import OpenAI
            self.client = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)

    def chat(self, prompt: str, system: str = "") -> str:
        if self.use_mock:
            return self._mock(prompt)
        messages = ([{"role": "system", "content": system}] if system else [])
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(
            model=MODEL_NAME, messages=messages, temperature=0.3
        )
        return resp.choices[0].message.content

    def _mock(self, prompt: str) -> str:
        time.sleep(0.02)
        # 决策
        if "自动工具调用能力的AI Agent" in prompt or "需要调用哪个工具" in prompt:
            user_task = self._extract_after(prompt, "用户任务：", prompt)
            decision = MockToolDecider.decide(user_task)
            return json.dumps(decision, ensure_ascii=False)
        # 反思工具结果
        if "工具执行结果：" in prompt:
            task = self._extract_after(prompt, "用户任务：", prompt)
            tool_result = prompt.split("工具执行结果：", 1)[1].split("请根据工具结果", 1)[0].strip()
            return (f"已根据工具结果完成任务「{task[:40]}」。\n\n"
                    f"🔧 工具执行结果：\n{tool_result[:500]}\n\n"
                    f"✅ 结论：工具调用成功，结果已纳入最终回答。")
        return f"[模拟回答] {prompt[:50]}..."

    @staticmethod
    def _extract_after(text: str, marker: str, default: str) -> str:
        if marker in text:
            return text.split(marker, 1)[1].split("\n")[0].strip()
        return default


# ======================================================================
# ToolAgent
# ======================================================================

class ToolAgent:
    """具备自动工具调用能力的Agent"""
    
    def __init__(self):
        self.history: List[Dict] = []
        self.llm = LLMClient()
    
    def load_history(self, history_list: List[Dict]):
        self.history = compress_history(history_list or [])
    
    def build_system_prompt(self) -> str:
        return """你是一个具备自动工具调用能力的AI Agent。
请根据用户任务自主判断：
1. 是否需要调用工具；
2. 需要调用哪个工具；
3. 需要传入什么参数。

如果你认为不需要调用工具，请直接给出自然语言回答。
如果你认为需要调用工具，请严格返回以下JSON格式：
{"tool_call": true, "tool_name": "工具名称", "tool_args": {"参数名": "参数值"}}

不要在JSON外添加多余解释。"""
    
    def decide_tool(self, user_input: str) -> Dict[str, Any]:
        """让Agent自主决定是否调用工具"""
        if USE_MOCK:
            return MockToolDecider.decide(user_input)
        
        tools_desc = tool_manager.get_tools_description()
        context = f"历史对话：{build_context(self.history)}\n" if self.history else ""
        prompt = f"{self.build_system_prompt()}\n\n{tools_desc}\n\n{context}用户任务：{user_input}"
        content = self.llm.chat(prompt)
        try:
            decision = json.loads(content)
            if decision.get("tool_call"):
                return decision
        except json.JSONDecodeError:
            pass
        return {"tool_call": False, "answer": content}
    
    def execute_tool_call(self, decision: Dict[str, Any]) -> str:
        return tool_manager.execute_tool(decision["tool_name"], decision.get("tool_args", {}))
    
    def reflect_tool_result(self, user_input: str, tool_result: str) -> str:
        return self.llm.chat(f"""用户任务：{user_input}

工具执行结果：
{tool_result}

请根据工具结果，给用户一个清晰、完整的最终回答。""")
    
    def run(self, user_input: str, history_list: List[Dict]) -> Dict[str, Any]:
        self.load_history(history_list)
        decision = self.decide_tool(user_input)
        
        if not decision.get("tool_call"):
            return {"tool_call": False, "final_answer": decision.get("answer", "")}
        
        tool_result = self.execute_tool_call(decision)
        
        # 链式：先算后写（文章测试3的场景）
        next_write = decision.get("_next_write")
        if next_write and str(tool_result).startswith("计算结果"):
            self.execute_tool_call({
                "tool_call": True,
                "tool_name": "write_file",
                "tool_args": {
                    "path": next_write["path"],
                    "content": next_write["content_template"].format(
                        result=tool_result.split("=")[-1].strip()),
                },
            })
        
        final_answer = self.reflect_tool_result(user_input, tool_result)
        return {
            "tool_call": True,
            "tool_name": decision["tool_name"],
            "tool_args": decision.get("tool_args", {}),
            "tool_result": tool_result,
            "final_answer": final_answer,
        }


tool_agent = ToolAgent()
