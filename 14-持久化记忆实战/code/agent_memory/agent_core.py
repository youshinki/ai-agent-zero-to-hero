#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第14篇配套完整项目代码 · agent_core.py
升级版：支持多轮上下文记忆的 Agent（规划/执行/反思都带历史）
==========================================================================
"""

import re
import time
from typing import Any, Dict, List

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
        history_text = self._extract_history(prompt)
        user_turn = self._extract_task(prompt)

        if "任务规划师" in prompt:
            return (f"【任务核心目标】\n结合历史理解当前需求：{user_turn}\n\n"
                    f"【任务拆解步骤】\n1. 回顾历史要点\n2. 对齐当前需求\n"
                    f"3. 生成连贯内容\n4. 自检\n\n"
                    f"【执行注意事项】\n不要遗忘上文，保持连贯")
        if "内容审核师" in prompt:
            memory_note = "已参考历史对话" if history_text else "无历史（首轮）"
            return (f"【问题清单】\n1. 连贯性：{memory_note} ✓\n2. 是否遗忘上文：否 ✓\n"
                    f"3. 逻辑冲突：无 ✓\n\n"
                    f"【优化后的最终答案】\n" + self._compose_answer(user_turn, history_text))
        return self._compose_answer(user_turn, history_text)

    @staticmethod
    def _extract_history(prompt: str) -> str:
        m = re.search(r"历史对话记录：(.*?)(?=\n当前|\n请|\n用户需求)", prompt, re.S)
        return m.group(1).strip()[:400] if m else ""

    @staticmethod
    def _extract_task(prompt: str) -> str:
        for marker in ["\n用户需求：", "当前用户新需求：", "当前需求："]:
            if marker in prompt:
                return prompt.split(marker, 1)[1].split("\n")[0].strip()
        if "用户需求：" in prompt:
            return prompt.split("用户需求：", 1)[1].split("\n")[0].strip()
        return prompt.strip()[:40]

    def _compose_answer(self, question: str, history: str) -> str:
        """模拟生成"带记忆"的连贯回答"""
        recalled = []
        if history:
            # 从历史中提取用户自述信息
            for pattern, label in [
                (r"我(?:是|叫)([^，。；]{1,20}(?:开发者|工程师|设计师|学生|经理|老师))", "身份"),
                (r"擅长([^，。；]{1,30})", "特长"),
                (r"我(?:喜欢|偏好)([^，。；]{1,30})", "偏好"),
            ]:
                m = re.search(pattern, history)
                if m:
                    recalled.append(f"{label}：{m.group(1)}")

        ans = f"针对「{question}」的回答：\n\n"
        if recalled:
            ans += "🧠 根据历史记忆，我了解到：\n" + "\n".join(f"- {r}" for r in recalled) + "\n\n"
        if "总结" in question and recalled:
            identity = recalled[0].split("：", 1)[1] if recalled else "用户"
            ans += (f"综合以上历史信息：你是{identity}，"
                    "本次回答已结合你此前提供的身份与特长，内容保持连贯。")
        else:
            ans += "已结合历史对话上下文作答，未出现前后矛盾或遗忘上文。"
        return ans


class BaseAgent:
    """多轮对话Agent"""
    
    def __init__(self):
        self.history: List[Dict] = []
        self.llm = LLMClient()

    def load_history(self, history_list: List[Dict]):
        self.history = history_list or []

    @staticmethod
    def _history_text(history: List[Dict], max_turns: int = 10) -> str:
        recent = history[-max_turns * 2:]
        lines = []
        for item in recent:
            role = "用户" if item.get("role") == "user" else "助手"
            lines.append(f"{role}：{item.get('content', '')[:200]}")
        return "\n".join(lines)

    def plan_task(self, user_input: str) -> str:
        context = f"历史对话记录：{self._history_text(self.history)}\n" if self.history else ""
        return self.llm.chat(f"""你是专业AI任务规划师，请结合历史对话，分步思考用户当前任务。
{context}
当前用户新需求：{user_input}
请严格输出：
1. 任务核心目标
2. 结合上下文的任务拆解步骤
3. 本次执行注意事项""")

    def execute_task(self, user_input: str, plan_result: str) -> str:
        context = f"历史对话记录：{self._history_text(self.history)}\n" if self.history else ""
        return self.llm.chat(f"""结合历史对话与任务规划，完整落地执行：
{context}
当前需求：{user_input}
任务规划：{plan_result}
输出完整、连贯、贴合上下文的最终内容。""")

    def reflect_task(self, user_input: str, raw_result: str) -> str:
        context = f"历史对话记录：{self._history_text(self.history)}\n" if self.history else ""
        return self.llm.chat(f"""结合历史对话自查本次回答是否连贯、合理：
{context}
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
