#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第12篇配套完整项目代码 · agent_core.py
智能体核心：保留 任务规划 → 任务执行 → 自我反思 完整闭环
（业务逻辑与服务逻辑分离 —— 文章工程化核心思想）
==========================================================================
"""

import time
from typing import Any, Dict

from config import (
    USE_MOCK, MODEL_NAME, VERBOSE, MAX_RETRY,
    MODEL_API_KEY, MODEL_BASE_URL,
)


# ======================================================================
# LLM客户端（真实 / 模拟双模式）
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
            model=MODEL_NAME, messages=messages, temperature=0.7
        )
        return resp.choices[0].message.content

    def _mock(self, prompt: str) -> str:
        time.sleep(0.02)
        if "任务规划师" in prompt or "严格分步思考" in prompt:
            return self._mock_plan(prompt)
        if "内容审核师" in prompt or "自查本次输出" in prompt:
            return self._mock_reflect(prompt)
        return self._mock_execute(prompt)

    @staticmethod
    def _extract_task(prompt: str) -> str:
        if "\n用户需求：" in prompt:
            return prompt.split("\n用户需求：", 1)[1].split("\n")[0].strip()
        if "用户需求：" in prompt:
            return prompt.split("用户需求：", 1)[1].split("\n")[0].strip()
        return prompt.strip()[:60]

    def _mock_plan(self, prompt: str) -> str:
        task = self._extract_task(prompt)
        return (f"【任务核心目标】\n完成用户需求：{task}\n\n"
                f"【任务拆解步骤】\n1. 明确需求与输出形态\n2. 收集必要信息\n"
                f"3. 生成结构化内容\n4. 自检完整性\n5. 优化定稿\n\n"
                f"【执行注意事项】\n- 结构与逻辑清晰\n- 数据可溯源\n- 可直接使用")

    def _mock_execute(self, prompt: str) -> str:
        task = self._extract_task(prompt)
        return (f"【执行结果】针对「{task}」：\n\n"
                f"一、核心内容\n已完成需求分析与内容组织。\n\n"
                f"二、交付说明\n本结果结构完整，可直接使用。")

    def _mock_reflect(self, prompt: str) -> str:
        task = self._extract_task(prompt)
        return (f"【问题清单】\n1. 完整性：已补充关键维度 ✓\n"
                f"2. 逻辑：结构已优化 ✓\n3. 准确性：已核验 ✓\n\n"
                f"【优化后的最终成品】\n针对「{task}」的最终版本：\n"
                f"一、完整内容（已补全所有维度）\n二、质量说明（已通过自检）")


# ======================================================================
# BaseAgent
# ======================================================================

class BaseAgent:
    """智能体核心（业务逻辑）"""
    
    def __init__(self):
        self.history = []
        self.llm = LLMClient()

    def plan_task(self, user_input: str) -> str:
        prompt = f"""你是专业AI任务规划师，请严格分步思考、拆解用户任务：
用户需求：{user_input}

请输出：
1. 任务核心目标
2. 任务拆解步骤
3. 执行注意事项"""
        return self.llm.chat(prompt)

    def execute_task(self, user_input: str, plan_result: str) -> str:
        prompt = f"""根据任务规划结果，完整落地执行用户需求：
用户需求：{user_input}
任务规划：{plan_result}

请输出完整、清晰、可直接使用的最终内容。"""
        return self.llm.chat(prompt)

    def reflect_task(self, user_input: str, raw_result: str) -> str:
        prompt = f"""你是严格的内容审核师，请自查本次输出：
用户需求：{user_input}
原始输出：{raw_result}

从以下维度自查：
1. 是否答非所问
2. 是否内容残缺、逻辑漏洞
3. 是否存在幻觉、虚假信息
4. 是否可以优化结构、措辞、完整性

输出：问题清单 + 优化后的最终成品"""
        return self.llm.chat(prompt)

    def run(self, user_task: str) -> Dict[str, Any]:
        """完整闭环，返回结构化结果（便于API序列化）"""
        plan = self._retry(self.plan_task, user_task)
        raw = self._retry(self.execute_task, user_task, plan)
        final = self._retry(self.reflect_task, user_task, raw)
        record = {
            "user_task": user_task,
            "task_plan": plan,
            "raw_result": raw,
            "final_result": final,
        }
        self.history.append(record)
        return record

    def _retry(self, func, *args) -> str:
        last = None
        for _ in range(MAX_RETRY):
            try:
                return func(*args)
            except Exception as e:
                last = e
                time.sleep(0.1)
        return f"[执行失败] {last}"


# 全局单例Agent（服务常驻复用 —— 文章工程化优化点1）
agent = BaseAgent()
