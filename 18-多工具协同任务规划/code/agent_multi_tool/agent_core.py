#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第18篇配套完整项目代码 · agent_core.py
多工具协同 + 任务规划 Agent：
  1. 自主任务拆解（JSON计划）
  2. 循环工具调用（后一步依赖前一步）
  3. 结果校验自查
  4. 汇总闭环交付
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
# 模拟规划器：把复合中文任务拆成有序步骤
# ======================================================================

class MockPlanner:
    """模拟AI自主任务拆解（真实模式由大模型输出JSON计划）"""
    
    @staticmethod
    def plan(user_input: str) -> Dict[str, Any]:
        text = user_input
        steps: List[Dict[str, Any]] = []
        
        # 识别计算
        m_calc = re.search(r"计算\s*([\d\.\s\+\-\*\/\(\)%]+)", text)
        # 识别写文件
        m_write = re.search(r"(?:保存到|写入到|写入|写到|保存至)\s*([^\s，。：:]+)(?:[：:](.+))?", text)
        # 识别读取
        m_read = re.search(r"(?:读取|查看|打开)\s*([^\s，。]+\.(?:txt|md|json|csv|log))", text)
        
        step_no = 1
        
        # 步骤1：读取（若有）
        if m_read:
            steps.append({
                "step": step_no, "desc": f"读取文件 {m_read.group(1)}",
                "tool_call": True, "tool_name": "read_file",
                "tool_args": {"path": m_read.group(1)},
            })
            step_no += 1
        
        # 步骤：计算（若有）
        calc_step_idx = None
        if m_calc:
            steps.append({
                "step": step_no, "desc": "计算数学表达式",
                "tool_call": True, "tool_name": "calculator",
                "tool_args": {"expression": m_calc.group(1).strip()},
            })
            calc_step_idx = len(steps) - 1
            step_no += 1
        
        # 步骤：文本生成（分析/总结/撰写）
        text_step_idx = None
        if any(k in text for k in ["分析", "总结", "撰写", "报告", "文案", "整理"]):
            steps.append({
                "step": step_no, "desc": "基于上一步结果生成分析总结内容",
                "tool_call": False, "tool_name": None, "tool_args": {},
            })
            text_step_idx = len(steps) - 1
            step_no += 1
        
        # 步骤：写文件（若有）
        if m_write:
            path = m_write.group(1).strip("，。")
            steps.append({
                "step": step_no, "desc": f"将结果保存到 {path}",
                "tool_call": True, "tool_name": "write_file",
                "tool_args": {"path": path, "content": ""},  # content 由前序结果填充
            })
        
        if len(steps) <= 1:
            # 单步或无需拆解
            if steps:
                return {"need_multi_step": False, **steps[0]}
            return {"need_multi_step": False,
                    "tool_call": False,
                    "desc": f"直接回答：{text}"}
        
        return {"need_multi_step": True, "task_steps": steps}


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
        # 汇总
        if "任务分步执行日志" in prompt:
            return self._mock_summary(prompt)
        # 文本生成（数据分析总结）
        if "数据分析" in prompt or "分析总结" in prompt:
            return self._mock_analysis(prompt)
        return f"[模拟生成] {prompt[:50]}..."

    def _mock_analysis(self, prompt: str) -> str:
        # 优先取等号后的结果
        value = "未知"
        m = re.search(r"=\s*([\-\d\.]+)", prompt)
        if m:
            value = m.group(1)
        else:
            m = re.search(r"([\-\d\.]+)\s*$", prompt)
            if m:
                value = m.group(1)
        return (f"数据分析总结\n\n"
                f"1. 计算结论：本次计算得到的结果为 {value}。\n"
                f"2. 数据分析：该数值反映了核心业务指标的增长规模，具备参考价值。\n"
                f"3. 建议：结合历史数据对比，持续跟踪该指标变化，及时调整策略。")

    def _mock_summary(self, prompt: str) -> str:
        log_part = prompt.split("任务分步执行日志", 1)[1]
        log_text = log_part.split("请基于以上完整执行流程", 1)[0].strip()
        return (f"全流程执行完成，结果如下：\n\n{log_text[:800]}\n\n"
                f"✅ 多步骤协同执行成功，所有步骤结果已串联并交付。")


# ======================================================================
# MultiToolAgent
# ======================================================================

class MultiToolAgent:
    """具备任务规划、多工具协同执行能力的高级Agent"""
    
    def __init__(self):
        self.history: List[Dict] = []
        self.max_iter = 5   # 最大迭代次数，防死循环
        self.llm = LLMClient()
        self.last_plan: Dict[str, Any] = {}
    
    def load_history(self, history_list: List[Dict]):
        self.history = compress_history(history_list or [])
    
    def build_planning_prompt(self) -> str:
        tools_desc = tool_manager.get_tools_description()
        return f"""你是具备任务规划、多工具协同执行能力的高级AI Agent。
可用工具如下：
{tools_desc}

请严格遵循规则：
1. 接收用户复杂任务后，自主拆解为有序子任务列表
2. 判断每个子任务是否需要工具、需要哪个工具、对应参数
3. 无需工具的子任务直接生成结果，需要工具的严格输出调用格式
4. 按顺序分步执行，依托上一步结果完成下一步操作
5. 最终汇总所有步骤结果，生成完整交付内容

输出规则：
如果需要多步工具协同，请输出JSON格式的任务计划：
{{
  "need_multi_step": true,
  "task_steps": [
    {{"step": 1, "desc": "子任务描述", "tool_call": true, "tool_name": "工具名", "tool_args": {{}}}}
  ]
}}

如果仅需单步操作，直接输出单工具调用JSON或自然语言答案。
禁止多余解释、禁止Markdown格式。"""
    
    def plan_task(self, user_input: str) -> Dict[str, Any]:
        """自主规划任务，拆解多步骤流程"""
        if USE_MOCK or not self.llm.client:
            plan = MockPlanner.plan(user_input)
        else:
            context = f"历史对话上下文：{build_context(self.history)}\n" if self.history else ""
            prompt = f"{self.build_planning_prompt()}\n{context}用户最终任务：{user_input}"
            content = self.llm.chat(prompt).strip()
            try:
                plan = json.loads(content)
            except json.JSONDecodeError:
                plan = {"need_multi_step": False, "content": content}
        self.last_plan = plan
        return plan
    
    def execute_single_step(self, step: Dict[str, Any],
                            context_text: str = "") -> str:
        """执行单步子任务"""
        if not step.get("tool_call"):
            # 无需工具：生成文本内容（可依赖前序结果）
            prompt = f"请基于以下信息生成内容：\n{context_text}\n\n任务：{step.get('desc', '')}"
            return self.llm.chat(prompt).strip()
        
        tool_name = step.get("tool_name")
        tool_args = dict(step.get("tool_args", {}))
        
        # 关键：后一步依赖前一步结果
        if tool_name == "write_file" and (not tool_args.get("content")):
            tool_args["content"] = context_text or "（空内容）"
        if tool_name == "write_file" and tool_args.get("content") == "":
            tool_args["content"] = context_text
        
        return tool_manager.execute_tool(tool_name, tool_args)
    
    def iterate_execute(self, task_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """循环迭代执行多步骤任务（后一步拿到前一步结果）"""
        steps = task_plan.get("task_steps", [])
        execute_log: List[Dict[str, Any]] = []
        context = ""
        
        for idx, step in enumerate(steps[:self.max_iter]):
            step_res = self.execute_single_step(step, context)
            execute_log.append({
                "step": step.get("step", idx + 1),
                "step_desc": step.get("desc", ""),
                "tool_name": step.get("tool_name") or "无",
                "result": step_res,
            })
            # 结果传递给下一步
            context = step_res
            print(f"   → 步骤{step.get('step', idx+1)} 完成：{str(step_res)[:60]}")
        
        return execute_log
    
    def summary_result(self, user_input: str,
                       execute_log: List[Dict[str, Any]]) -> str:
        """汇总多步骤执行结果，生成最终答案"""
        log_json = json.dumps(execute_log, ensure_ascii=False, indent=2)
        if USE_MOCK or not self.llm.client:
            return self.llm.chat(f"任务分步执行日志\n{log_json}\n\n请基于以上完整执行流程生成最终回答。")
        return self.llm.chat(f"""用户任务：{user_input}
任务分步执行日志：
{log_json}

请基于以上完整执行流程，整理出清晰、完整、结构化的最终回答，
梳理每一步操作、核心结果、最终结论，输出用户可直接使用的交付内容。""")
    
    def run(self, user_input: str,
            history_list: List[Dict]) -> Dict[str, Any]:
        self.load_history(history_list)
        print(f"\n🤖 MultiToolAgent | {user_input}")
        
        # 1. 自主任务规划
        print("📋 [规划] 拆解任务...")
        task_plan = self.plan_task(user_input)
        
        if not task_plan.get("need_multi_step"):
            print("   判断：单步任务")
            single = self.execute_single_step(task_plan)
            final = self.summary_result(user_input, [{
                "step": 1, "step_desc": task_plan.get("desc", user_input),
                "tool_name": task_plan.get("tool_name") or "无", "result": single,
            }])
            return {"multi_step": False, "final_answer": final}
        
        # 2. 多步骤迭代执行
        print(f"   判断：多步任务（{len(task_plan.get('task_steps', []))}步）")
        execute_log = self.iterate_execute(task_plan)
        
        # 3. 汇总生成最终交付
        print("📝 [汇总] 生成最终交付...")
        final_answer = self.summary_result(user_input, execute_log)
        
        return {
            "multi_step": True,
            "step_count": len(execute_log),
            "execute_log": execute_log,
            "final_answer": final_answer,
        }


agent = MultiToolAgent()
