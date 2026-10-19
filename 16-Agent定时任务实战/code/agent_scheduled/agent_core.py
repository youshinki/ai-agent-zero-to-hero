#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第15篇配套完整项目代码 · agent_core.py
适配压缩记忆的 Agent：load_history 时自动压缩
==========================================================================
"""

import time
from typing import Any, Dict, List

from config import USE_MOCK, MODEL_NAME, MAX_RETRY, MODEL_API_KEY, MODEL_BASE_URL
from memory_utils import compress_history, build_context


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
        has_summary = "【历史对话摘要】" in prompt
        task = self._extract_task(prompt)

        if "任务规划师" in prompt:
            note = "（已使用压缩摘要）" if has_summary else "（无历史）"
            return (f"【任务核心目标】\n完成：{task}{note}\n\n"
                    f"【任务拆解步骤】\n1. 回顾记忆\n2. 对齐需求\n3. 生成内容\n4. 自检\n\n"
                    f"【执行注意事项】\n保持连贯")
        if "内容审核师" in prompt:
            return (f"【问题清单】\n1. 连贯性：{'已基于压缩摘要' if has_summary else '首轮无历史'} ✓\n"
                    f"2. 逻辑冲突：无 ✓\n\n"
                    f"【优化后的最终答案】\n针对「{task}」：\n"
                    f"{'已结合历史摘要作答，远期要点未丢失。' if has_summary else '首轮回答。'}")
        return f"针对「{task}」的执行结果：已结合{'压缩记忆' if has_summary else '当前上下文'}完成。"

    @staticmethod
    def _extract_task(prompt: str) -> str:
        for marker in ["\n用户需求：", "当前用户新需求：", "当前需求："]:
            if marker in prompt:
                return prompt.split(marker, 1)[1].split("\n")[0].strip()
        if "用户需求：" in prompt:
            return prompt.split("用户需求：", 1)[1].split("\n")[0].strip()
        return prompt.strip()[:40]


class BaseAgent:
    def __init__(self):
        self.history: List[Dict] = []
        self.llm = LLMClient()

    def load_history(self, history_list: List[Dict]):
        """载入历史时自动压缩（核心）"""
        self.history = compress_history(history_list or [])

    def _context(self) -> str:
        if not self.history:
            return ""
        return f"历史对话记录：{build_context(self.history)}\n"

    def plan_task(self, user_input: str) -> str:
        return self.llm.chat(f"""你是专业AI任务规划师，请结合历史对话分步思考当前任务。
{self._context()}
当前用户新需求：{user_input}
请严格输出：1.任务核心目标 2.任务拆解步骤 3.本次执行注意事项""")

    def execute_task(self, user_input: str, plan_result: str) -> str:
        return self.llm.chat(f"""结合历史对话与任务规划，完整落地执行：
{self._context()}
当前需求：{user_input}
任务规划：{plan_result}
输出完整、连贯、贴合上下文的最终内容。""")

    def reflect_task(self, user_input: str, raw_result: str) -> str:
        return self.llm.chat(f"""结合历史对话自查本次回答是否连贯合理：
{self._context()}
当前需求：{user_input}
原始输出：{raw_result}
自查：连贯性、完整性、是否遗忘上文、是否逻辑冲突
输出：问题清单 + 最终优化答案""")

    def run_with_history(self, user_task: str, history_list: List[Dict]) -> Dict[str, Any]:
        self.load_history(history_list)
        plan = self._retry(self.plan_task, user_task)
        raw = self._retry(self.execute_task, user_task, plan)
        final = self._retry(self.reflect_task, user_task, raw)
        return {
            "user_task": user_task,
            "plan": plan,
            "raw_result": raw,
            "final_result": final,
        }

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
