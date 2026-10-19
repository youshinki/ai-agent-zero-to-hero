#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第13篇配套完整项目代码 · agent_core.py
Agent核心：规划 → 执行 → 反思（保持与第12篇一致，流式升级不改核心）
==========================================================================
"""

import time
from typing import Any, Dict

from config import (
    USE_MOCK, MODEL_NAME, MAX_RETRY,
    MODEL_API_KEY, MODEL_BASE_URL,
)


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
            task = self._extract_task(prompt)
            return (f"【任务核心目标】\n完成：{task}\n\n"
                    f"【任务拆解步骤】\n1. 明确目标\n2. 收集信息\n3. 生成内容\n4. 自检优化\n\n"
                    f"【执行注意事项】\n结构清晰、可直接使用")
        if "内容审核师" in prompt or "自查本次输出" in prompt:
            task = self._extract_task(prompt)
            return (f"【问题清单】\n1. 完整性：已补全 ✓\n2. 逻辑：已优化 ✓\n\n"
                    f"【优化后的最终成品】\n针对「{task}」：\n\n"
                    f"一、核心结论\n已按规划完成内容组织。\n\n"
                    f"二、执行要点\n1. 先明确目标\n2. 再收集信息\n3. 最后自检\n\n"
                    f"三、交付说明\n本结果已通过自我审核，可直接使用。")
        task = self._extract_task(prompt)
        return f"【执行结果】针对「{task}」的完整内容：\n一、需求分析\n二、核心内容\n三、总结"

    @staticmethod
    def _extract_task(prompt: str) -> str:
        if "\n用户需求：" in prompt:
            return prompt.split("\n用户需求：", 1)[1].split("\n")[0].strip()
        if "用户需求：" in prompt:
            return prompt.split("用户需求：", 1)[1].split("\n")[0].strip()
        return prompt.strip()[:50]


class BaseAgent:
    def __init__(self):
        self.history = []
        self.llm = LLMClient()

    def plan_task(self, user_input: str) -> str:
        return self.llm.chat(f"""你是专业AI任务规划师，请严格分步思考、拆解用户任务：
用户需求：{user_input}

请输出：
1. 任务核心目标
2. 任务拆解步骤
3. 执行注意事项""")

    def execute_task(self, user_input: str, plan_result: str) -> str:
        return self.llm.chat(f"""根据任务规划结果，完整落地执行用户需求：
用户需求：{user_input}
任务规划：{plan_result}

请输出完整、清晰、可直接使用的最终内容。""")

    def reflect_task(self, user_input: str, raw_result: str) -> str:
        return self.llm.chat(f"""你是严格的内容审核师，请自查本次输出：
用户需求：{user_input}
原始输出：{raw_result}

从以下维度自查：
1. 是否答非所问
2. 是否内容残缺、逻辑漏洞
3. 是否存在幻觉、虚假信息
4. 是否可以优化结构、措辞、完整性

输出：问题清单 + 优化后的最终成品""")

    def run(self, user_task: str) -> Dict[str, Any]:
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


agent = BaseAgent()
