#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第9篇配套完整项目代码 · agent_core.py
融合RAG能力的Agent：规划 → 知识库增强执行 → 反思
==========================================================================
"""

import time
from typing import Dict, List

from config import USE_MOCK, MODEL_NAME, VERBOSE


# ======================================================================
# 统一 LLM 客户端（真实 / 模拟双模式）
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
        # 规划
        if "任务规划师" in prompt or "严格分步思考" in prompt:
            return ("【任务核心目标】\n基于私有资料回答用户问题\n\n"
                    "【任务拆解步骤】\n1. 检索知识库相关片段\n2. 核对资料是否覆盖问题\n"
                    "3. 基于资料组织答案\n4. 标注依据、不编造\n\n"
                    "【执行注意事项】\n只使用私有资料内容，禁止幻觉")
        # 反思
        if "内容审核" in prompt or "自查本次基于知识库的回答" in prompt:
            return ("【问题清单】\n1. 回答仅覆盖资料中出现的信息 ✓\n"
                    "2. 无编造内容 ✓\n3. 已给出结论与依据 ✓\n\n"
                    "【优化后的最终答案】\n" + self._extract_answer(prompt))
        # 增强执行
        if "私有参考资料" in prompt:
            return self._grounded_answer(prompt)
        return f"[模拟回答] 针对问题：{prompt[:40]}..."

    @staticmethod
    def _extract_answer(prompt: str) -> str:
        """从执行提示词中提取原始回答"""
        if "原始输出：" in prompt:
            return prompt.split("原始输出：", 1)[1].split("\n\n自查维度")[0].strip()
        return "(无原始输出)"

    def _grounded_answer(self, prompt: str) -> str:
        """基于参考资料生成答案（模拟）"""
        question = ""
        context = ""
        # 提示词中「用户需求：」可能出现两次，取换行后的那次
        if "\n用户需求：" in prompt:
            question = prompt.split("\n用户需求：", 1)[1].split("\n")[0].strip()
        elif "用户需求：" in prompt:
            question = prompt.split("用户需求：", 1)[1].split("\n")[0].strip()
        if "私有参考资料：" in prompt:
            context = prompt.split("私有参考资料：", 1)[1].split("严格基于")[0].strip()
        # 从上下文截取一段作为依据
        excerpt = context.replace("\n", " ").strip()[:160]
        return (f"根据私有知识库资料，回答「{question}」：\n\n"
                f"{excerpt}\n\n"
                f"📎 以上内容均来自知识库文档，未做资料外补充。")


# ======================================================================
# 融合RAG的 Agent
# ======================================================================

class BaseAgent:
    """基础AI Agent（已融合RAG知识库能力）"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.history: List[Dict] = []
        self.knowledge_context = ""   # 注入的私有知识
    
    # ----- 注入检索到的私有知识 -----
    def set_knowledge(self, context: str):
        self.knowledge_context = context or ""
    
    # ----- 1. 任务规划 -----
    def plan_task(self, user_input: str) -> str:
        prompt = f"""你是专业AI任务规划师，请严格分步思考、拆解用户任务：
用户需求：{user_input}

请输出：
1. 任务核心目标
2. 任务拆解步骤
3. 执行注意事项"""
        return self.llm.chat(prompt, system="你是严谨的任务规划专家")
    
    # ----- 2. 融合知识库执行 -----
    def execute_task(self, user_input: str, plan_result: str) -> str:
        prompt = f"""请结合私有知识库内容，落地执行用户需求：
用户需求：{user_input}
任务规划：{plan_result}
私有参考资料：{self.knowledge_context}

严格基于参考资料回答，禁止编造、禁止幻觉、禁止脱离文档内容。
输出完整、清晰、准确的答案。"""
        return self.llm.chat(prompt, system="你是基于知识库问答的专家")
    
    # ----- 3. 反思纠错 -----
    def reflect_task(self, user_input: str, raw_result: str) -> str:
        prompt = f"""你是严格的内容审核师，请自查本次基于知识库的回答：
用户需求：{user_input}
原始输出：{raw_result}

自查维度：
1. 是否脱离私有文档内容、存在幻觉编造
2. 是否答非所问、遗漏关键信息
3. 逻辑是否通顺、内容是否完整

输出：问题清单 + 优化后的最终答案"""
        return self.llm.chat(prompt, system="你是严格的内容审核专家")
    
    # ----- 4. 完整运行闭环 -----
    def run(self, user_task: str, rag, verbose: bool = VERBOSE) -> str:
        if verbose:
            print(f"\n{'='*60}")
            print(f"🤖 RAG Agent 处理：{user_task}")
            print(f"{'='*60}")
        
        # 【1/3】规划
        if verbose:
            print("\n【1/3】任务规划中...")
        plan = self.plan_task(user_task)
        
        # 检索知识库
        if verbose:
            print("\n🔍 检索私有知识库...")
        hits = rag.search_relevant(user_task, return_scores=True)
        if hits and isinstance(hits[0], tuple):
            context = "\n\n".join(h[0] for h in hits)
            hit_count = len(hits)
            top_score = hits[0][1]
        else:
            context = rag.search_relevant(user_task)
            hit_count = 1
            top_score = 0.0
        self.set_knowledge(context)
        if verbose:
            print(f"   命中{hit_count}个相关片段（最高相似度{top_score:.3f}）")
        
        # 【2/3】执行
        if verbose:
            print("\n【2/3】结合知识库执行中...")
        raw_result = self.execute_task(user_task, plan)
        
        # 【3/3】反思
        if verbose:
            print("\n【3/3】反思优化纠错中...")
        final_result = self.reflect_task(user_task, raw_result)
        
        self.history.append({
            "task": user_task,
            "context_len": len(context),
            "final": final_result[:200],
        })
        
        return final_result
