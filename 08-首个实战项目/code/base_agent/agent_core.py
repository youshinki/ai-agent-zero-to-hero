#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第8篇配套完整项目代码
首个实战项目：从零手写基础AI Agent
==========================================================================

本文件为 agent_core.py —— Agent核心逻辑：思考、执行、反思
包含三大核心模块：
  1. 思维规划（CoT分步拆解）
  2. 任务执行（生成原始结果）
  3. 自我反思纠错（Reflexion校验优化）
==========================================================================
"""

import json
import time
from typing import Dict, List, Optional, Tuple

from config import (
    MODEL_API_KEY, MODEL_BASE_URL, MODEL_NAME,
    USE_MOCK, MAX_THOUGHT_STEPS, MAX_RETRY, MAX_HISTORY, VERBOSE,
)


# ======================================================================
# 一、LLM 客户端层（真实API / 模拟后端 双模式）
# ======================================================================

class LLMClient:
    """统一的大模型客户端
    
    USE_MOCK=True 时使用内置模拟实现，保证零依赖可运行；
    USE_MOCK=False 时调用真实 OpenAI 兼容接口。
    """
    
    def __init__(self):
        self.use_mock = USE_MOCK
        self.client = None
        if not self.use_mock:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)
            except ImportError:
                print("⚠️ 未安装 openai 包，自动切换为模拟模式。安装: pip install openai")
                self.use_mock = True
    
    def chat(self, prompt: str, system: str = "") -> str:
        """统一对话接口"""
        if self.use_mock:
            return self._mock_chat(prompt, system)
        else:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            resp = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.7,
            )
            return resp.choices[0].message.content
    
    # ----- 模拟实现：根据提示词类型返回结构化结果 -----
    def _mock_chat(self, prompt: str, system: str = "") -> str:
        """模拟LLM：按提示词语义返回合理结果，保证流程可跑通

        注意：必须优先判断「任务规划师 / 审核师」这类角色指令，
        因为执行和反思提示词里会内嵌"任务规划"等文字，容易误匹配。
        """
        time.sleep(0.05)  # 模拟网络延迟
        
        # 优先级1：反思（审核角色）
        if "内容审核" in prompt or "内容审核师" in prompt or "自查本次输出" in prompt:
            return self._mock_reflect(prompt)
        # 优先级2：规划（规划师角色）
        if "任务规划师" in prompt or "请严格分步思考" in prompt:
            return self._mock_plan(prompt)
        # 优先级3：执行
        return self._mock_execute(prompt)
    
    def _mock_plan(self, prompt: str) -> str:
        """模拟CoT规划结果"""
        task = self._extract_task(prompt)
        return f"""【任务核心目标】
完成用户需求：{task}

【任务拆解步骤】
1. 明确需求边界与输出形式
2. 收集并整理必要信息
3. 按目标结构生成初稿内容
4. 自检内容完整性与准确性
5. 优化措辞并输出最终成品

【执行注意事项】
- 保证内容结构清晰、逻辑连贯
- 数据必须可溯源，不编造
- 输出需可直接使用，无需二次加工"""
    
    def _mock_execute(self, prompt: str) -> str:
        """模拟执行结果"""
        task = self._extract_task(prompt)
        
        if "周报" in task or "总结" in task:
            return """【本周工作总结】
一、重点工作完成情况
1. 完成AI客服系统需求评审，确认3个核心模块
2. 推进知识库数据清洗，完成80%标注工作
3. 修复3个P2级线上Bug
4. 输出Q2产品路线图V2

二、存在的问题
第三方支付接口集成进度滞后，原定1月底现预计2月中旬。

三、下周计划
1. 完成知识库全量清洗
2. 启动AI客服系统开发
3. 跟进支付接口联调"""
        
        if "方案" in task or "技术" in task:
            return """【技术方案】
一、架构设计
采用分层架构：接入层 → 业务层 → 模型层 → 数据层

二、核心模块
1. 对话管理模块
2. 知识库检索模块
3. 工具调用模块
4. 监控告警模块

三、实施计划
一期：核心对话能力（2周）
二期：知识库集成（2周）
三期：上线与优化（1周）"""
        
        return f"""【执行结果】
针对任务「{task}」的完整产出：

1. 已完成需求分析
2. 已生成核心内容
3. 已整理为可交付格式"""

    def _extract_task(self, prompt: str) -> str:
        """从提示词中提取用户任务"""
        for marker in ["用户需求：", "用户需求:", "任务：", "问题："]:
            if marker in prompt:
                part = prompt.split(marker, 1)[1]
                # 取第一行或前40字
                return part.strip().split("\n")[0][:60]
        return prompt.strip()[:60]
    
    def _mock_reflect(self, prompt: str) -> str:
        """模拟反思优化结果"""
        task = self._extract_task(prompt)
        return f"""【问题清单】
1. 【完整性】缺少具体的量化数据支撑
2. 【结构】章节之间的过渡不够自然
3. 【准确性】部分表述缺少依据

【优化后的最终成品】
针对「{task}」的优化版本：

一、完整内容（已补全所有维度）
- 已补充量化指标和数据来源
- 已优化逻辑结构与过渡
- 已核验事实准确性

二、交付说明
本结果已通过自我审核，可直接使用。
（模拟模式说明：真实模式下由大模型执行同样的"执行→审核→优化"流程）"""


# ======================================================================
# 二、Agent 核心类
# ======================================================================

class BaseAgent:
    """基础AI Agent —— 规划 → 执行 → 反思 完整闭环"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.history: List[Dict] = []   # 简短记忆
        self.step_count = 0
    
    # ---------- 1. 思维规划：CoT分步拆解 ----------
    def plan_task(self, user_input: str) -> str:
        """任务规划：让模型先思考再动手"""
        prompt = f"""你是专业AI任务规划师，请严格分步思考、拆解用户任务：
用户需求：{user_input}

请输出：
1. 任务核心目标
2. 任务拆解步骤
3. 执行注意事项"""
        return self.llm.chat(prompt, system="你是严谨的任务规划专家")
    
    # ---------- 2. 任务执行：生成原始结果 ----------
    def execute_task(self, user_input: str, plan_result: str) -> str:
        """任务执行：按规划生成内容"""
        prompt = f"""根据任务规划结果，完整落地执行用户需求：
用户需求：{user_input}
任务规划：{plan_result}

请输出完整、清晰、可直接使用的最终内容。"""
        return self.llm.chat(prompt, system="你是专业的执行专家")
    
    # ---------- 3. 自我反思：Reflexion校验优化 ----------
    def reflect_task(self, user_input: str, raw_result: str) -> str:
        """自我反思：以审核者身份检查并给出优化成品"""
        prompt = f"""你是严格的内容审核师，请自查本次输出：
用户需求：{user_input}
原始输出：{raw_result}

从以下维度自查：
1. 是否答非所问
2. 是否内容残缺、逻辑漏洞
3. 是否存在幻觉、虚假信息
4. 是否可以优化结构、措辞、完整性

输出：问题清单 + 优化后的最终成品"""
        return self.llm.chat(prompt, system="你是严格的内容审核专家")
    
    # ---------- 4. 完整运行闭环 ----------
    def run(self, user_task: str) -> str:
        """Agent完整运行：规划 → 执行 → 反思"""
        self.step_count += 1
        step = self.step_count
        
        if VERBOSE:
            print(f"\n{'='*60}")
            print(f"🤖 第{step}次任务 | {user_task}")
            print(f"{'='*60}")
        
        # 【1/3】规划
        if VERBOSE:
            print("\n【1/3】任务规划中...")
        plan = self._retry(self.plan_task, user_task)
        if VERBOSE:
            print(f"✅ 规划完成（{len(plan)}字）")
            print(f"   {plan.split(chr(10))[0]}")
        
        # 【2/3】执行
        if VERBOSE:
            print("\n【2/3】任务执行中...")
        raw_result = self._retry(self.execute_task, user_task, plan)
        if VERBOSE:
            print(f"✅ 执行完成（{len(raw_result)}字）")
        
        # 【3/3】反思
        if VERBOSE:
            print("\n【3/3】自我反思优化中...")
        final_result = self._retry(self.reflect_task, user_task, raw_result)
        if VERBOSE:
            print(f"✅ 反思优化完成（{len(final_result)}字）")
        
        # 保存简短记忆
        self.history.append({
            "task": user_task,
            "plan": plan[:200],
            "raw": raw_result[:200],
            "final": final_result[:200],
        })
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]
        
        return final_result
    
    def _retry(self, func, *args) -> str:
        """带重试的执行（新手调试必备）"""
        last_err = None
        for attempt in range(1, MAX_RETRY + 1):
            try:
                return func(*args)
            except Exception as e:
                last_err = e
                if VERBOSE:
                    print(f"   ⚠️ 第{attempt}次失败：{e}，重试中...")
                time.sleep(0.2 * attempt)
        # 最终兜底：返回错误说明，不让程序崩溃
        return f"[执行失败] 已重试{MAX_RETRY}次，最后一次错误：{last_err}"
    
    # ---------- 5. 记忆查询 ----------
    def get_history(self) -> List[Dict]:
        return self.history
