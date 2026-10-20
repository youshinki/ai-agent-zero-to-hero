#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第10篇配套完整项目代码 · agent_core.py
融合 RAG + 工具调用 的办公Agent

Function Call 三要素：
  1. 工具定义 → tool_core.TOOLS_DEFINITION
  2. 模型决策 → decide_and_execute_tool
  3. 工具执行 → tool_core.execute_tool
==========================================================================
"""

import json
import time
from typing import List, Optional

from config import USE_MOCK, MODEL_NAME, VERBOSE
from tool_core import (TOOLS_DEFINITION, execute_tool)


# ======================================================================
# 模拟工具决策引擎（真实模式下由大模型决策）
# ======================================================================

class MockToolDecider:
    """模拟大模型判断是否调用工具、调用哪个、参数是什么"""
    
    @staticmethod
    def decide(user_input: str):
        """返回 [(tool_name, args_dict), ...] 或 []"""
        import re
        text = user_input.lower()
        
        # 时间
        if any(k in text for k in ["几点", "现在时间", "今天几号", "日期", "星期几", "现在几点"]):
            return [("get_current_time", {})]
        
        # 读取文件
        if any(k in text for k in ["读取", "查看文件", "打开文件", "分析文件", "读一下", "读文件"]):
            path = "./docs/report.txt"
            for token in user_input.split():
                # 只去掉尾部的中文标点，不要去掉开头的 "./"
                token = token.rstrip("，。,.")
                if token.startswith("./") or token.startswith("/"):
                    path = token
                    break
                if token.endswith(".txt") and "/" in token:
                    path = token
                    break
            return [("read_file_content", {"file_path": path})]
        
        # 计算：必须有明确的计算意图或算术表达式
        has_calc_intent = any(k in text for k in ["计算", "算一下", "算算", "帮我算", "等于多少", "求值"])
        has_arith = bool(re.search(r"\d+(\.\d+)?\s*[\+\-\*/]\s*\d", user_input))
        if has_calc_intent or has_arith:
            expr_match = re.search(r"[\d\.\s\+\-\*\/\(\)%]+", user_input)
            expr = expr_match.group().strip() if expr_match else "100 * 0.85"
            if not expr:
                expr = "100 * 0.85"
            return [("calculate", {"expression": expr})]
        
        return []


# ======================================================================
# LLM 客户端（真实 / 模拟）
# ======================================================================

class LLMClient:
    def __init__(self):
        self.use_mock = USE_MOCK
        self.client = None
        if not self.use_mock:
            try:
                from openai import OpenAI
                from config import MODEL_API_KEY, MODEL_BASE_URL
                self.client = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)
            except ImportError:
                self.use_mock = True

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
        time.sleep(0.03)
        if "内容审核" in prompt or "自查本次回答" in prompt:
            return self._mock_reflect(prompt)
        if "用户需求：" in prompt and ("工具执行结果" in prompt or "参考资料" in prompt):
            return self._mock_answer(prompt)
        return f"[模拟回答] {prompt[:40]}..."

    def _mock_answer(self, prompt: str) -> str:
        question = ""
        if "\n用户需求：" in prompt:
            question = prompt.split("\n用户需求：", 1)[1].split("\n")[0].strip()
        elif "用户需求：" in prompt:
            question = prompt.split("用户需求：", 1)[1].split("\n")[0].strip()
        
        # 收集工具结果
        tool_part = ""
        if "工具执行结果：" in prompt:
            tool_part = prompt.split("工具执行结果：", 1)[1]
            if "参考资料：" in tool_part:
                tool_part = tool_part.split("参考资料：")[0]
            tool_part = tool_part.strip()
        
        knowledge = ""
        if "参考资料：" in prompt:
            knowledge = prompt.split("参考资料：", 1)[1].strip()[:160]
        
        parts = [f"针对「{question}」，回答如下："]
        if tool_part:
            parts.append(f"\n🔧 工具提供的事实依据：\n{tool_part[:300]}")
        if knowledge:
            parts.append(f"\n📚 知识库参考资料：\n{knowledge}")
        if not tool_part and not knowledge:
            parts.append("\n（本次任务无需工具，直接作答）")
        return "\n".join(parts)

    def _mock_reflect(self, prompt: str) -> str:
        return ("【问题清单】\n1. 工具结果是否被正确使用：已核对 ✓\n"
                "2. 是否存在幻觉：未编造 ✓\n3. 表达是否清晰：已优化 ✓\n\n"
                "【优化后的最终答案】\n" + self._extract_answer(prompt))

    @staticmethod
    def _extract_answer(prompt: str) -> str:
        if "原始输出：" in prompt:
            return prompt.split("原始输出：", 1)[1].split("\n\n自查维度")[0].strip()
        return "(无)"


# ======================================================================
# OfficeAgent：工具 + RAG 完整闭环
# ======================================================================

class OfficeAgent:
    """自动化办公Agent"""
    
    def __init__(self):
        self.history: List[dict] = []
        self.knowledge_context = ""
        self.llm = LLMClient()
    
    # ----- 注入RAG检索结果 -----
    def set_knowledge(self, context: str):
        self.knowledge_context = context or ""
    
    # ----- 1. 工具调用决策 + 执行 -----
    def decide_and_execute_tool(self, user_input: str) -> Optional[str]:
        if USE_MOCK:
            decisions = MockToolDecider.decide(user_input)
            if not decisions:
                return None
            results = []
            for name, args in decisions:
                print(f"  🛠 调用工具：{name} | 参数：{json.dumps(args, ensure_ascii=False)}")
                result = execute_tool(name, args)
                results.append(f"【{name}】\n{result}")
            return "\n\n".join(results)
        else:
            # 真实Function Call
            from config import MODEL_API_KEY, MODEL_BASE_URL
            from openai import OpenAI
            client = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)
            messages = [
                {"role": "system", "content": "你是智能办公助手，可按需调用工具完成任务。"},
                {"role": "user", "content": user_input},
            ]
            resp = client.chat.completions.create(
                model=MODEL_NAME, messages=messages,
                tools=TOOLS_DEFINITION, tool_choice="auto"
            )
            msg = resp.choices[0].message
            if not msg.tool_calls:
                return None
            from tool_core import execute_all_tool_calls
            return execute_all_tool_calls(msg.tool_calls)
    
    # ----- 2. 结合工具结果 + 知识库生成答案 -----
    def execute_task(self, user_input: str, tool_result: Optional[str]) -> str:
        knowledge_part = f"\n参考资料：{self.knowledge_context}" if self.knowledge_context else ""
        tool_part = f"\n工具执行结果：{tool_result}" if tool_result else ""
        prompt = f"""用户需求：{user_input}
{tool_part}
{knowledge_part}

请基于以上信息，完整、准确地回答用户问题。
如果工具结果中包含错误信息，请如实告知用户。"""
        return self.llm.chat(prompt, system="你是严谨的智能办公助手")
    
    # ----- 3. 自我反思 -----
    def reflect_task(self, user_input: str, raw_result: str) -> str:
        prompt = f"""你是内容审核师，请自查本次回答：
用户需求：{user_input}
原始输出：{raw_result}

自查维度：
1. 是否准确回答了用户问题
2. 是否存在幻觉或编造内容
3. 工具结果是否被正确使用
4. 逻辑是否通顺、表达是否清晰

输出：问题清单 + 优化后的最终答案"""
        return self.llm.chat(prompt, system="你是严格的内容审核专家")
    
    # ----- 完整运行闭环 -----
    def run(self, user_task: str, rag=None, verbose: bool = VERBOSE) -> str:
        if verbose:
            print(f"\n{'='*60}")
            print(f"🤖 办公Agent | {user_task}")
            print(f"{'='*60}")
        
        # 可选：先检索知识库
        if rag is not None:
            if verbose:
                print("\n🔍 检索知识库...")
            hits = rag.search_relevant(user_task, return_scores=True)
            if hits and isinstance(hits[0], tuple):
                context = "\n\n".join(h[0] for h in hits)
                if verbose:
                    print(f"   命中{len(hits)}个片段")
            else:
                context = ""
            self.set_knowledge(context)
        
        # 1. 工具决策
        if verbose:
            print("\n【1/3】判断是否需要调用工具...")
        tool_result = self.decide_and_execute_tool(user_task)
        if verbose:
            if tool_result:
                print(f"   工具执行完成（{len(tool_result)}字）")
            else:
                print("   判断：无需调用工具")
        
        # 2. 生成答案
        if verbose:
            print("\n【2/3】结合工具结果生成答案...")
        raw = self.execute_task(user_task, tool_result)
        
        # 3. 反思
        if verbose:
            print("\n【3/3】反思优化纠错...")
        final = self.reflect_task(user_task, raw)
        
        self.history.append({"task": user_task, "used_tool": bool(tool_result)})
        return final
