#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第19篇配套完整项目代码 · agent_core.py
自主纠错重试 Agent（五层容错闭环）：
  执行 → 校验 → 反思 → 修正 → 重试
==========================================================================
"""

import json
import os
import re
import time
from typing import Any, Dict, List

from config import USE_MOCK, MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL
from memory_utils import compress_history, build_context
from tools.tool_manager import create_default_tools


tool_manager = create_default_tools()


# ======================================================================
# 模拟规划器（复用第18篇思路，增加"错误场景"识别）
# ======================================================================

class MockPlanner:
    @staticmethod
    def plan(user_input: str) -> Dict[str, Any]:
        text = user_input
        steps: List[Dict[str, Any]] = []
        step_no = 1

        m_read = re.search(r"(?:读取|查看|打开)\s*([^\s，。]+\.(?:txt|md|json|csv|log))", text)
        if m_read:
            steps.append({
                "step": step_no, "desc": f"读取文件 {m_read.group(1)}",
                "tool_call": True, "tool_name": "read_file",
                "tool_args": {"path": m_read.group(1)},
            })
            step_no += 1

        m_calc = re.search(r"计算\s*([\d\.\s\+\-\*\/\(\)%]+)", text)
        if m_calc:
            steps.append({
                "step": step_no, "desc": "计算数学表达式",
                "tool_call": True, "tool_name": "calculator",
                "tool_args": {"expression": m_calc.group(1).strip()},
            })
            step_no += 1

        m_write = re.search(r"(?:保存到|写入到|写入|写到|保存至)\s*([^\s，。：:]+)(?:[：:](.+))?", text)
        if m_write:
            steps.append({
                "step": step_no, "desc": f"保存到 {m_write.group(1)}",
                "tool_call": True, "tool_name": "write_file",
                "tool_args": {"path": m_write.group(1).strip("，。"),
                              "content": (m_write.group(2) or "").strip()},
            })

        if len(steps) <= 1:
            if steps:
                return {"need_multi_step": False, **steps[0]}
            return {"need_multi_step": False, "tool_call": False,
                    "desc": f"直接回答：{text}"}
        return {"need_multi_step": True, "task_steps": steps}


# ======================================================================
# 模拟反思修正器：错误 → 修正后的步骤
# ======================================================================

class MockFixer:
    """模拟AI自主反思：分析错误原因并修正参数"""
    
    @staticmethod
    def fix(step: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        fixed = json.loads(json.dumps(step))  # 深拷贝
        tool = fixed.get("tool_name")
        args = fixed.setdefault("tool_args", {})
        
        # 文件不存在 → 自动补全为默认示例文件
        if "读" in error_msg and ("No such file" in error_msg or "找不到" in error_msg or "不存在" in error_msg):
            args["path"] = "auto_task_log/task_record.txt"
            print(f"      🔧 反思修正：路径改为 {args['path']}")
        
        # 参数缺失 → 补默认值
        elif tool == "write_file" and not args.get("path"):
            args["path"] = "output.txt"
            print(f"      🔧 反思修正：补全 path=output.txt")
        
        elif tool == "write_file" and not args.get("content"):
            args["content"] = "（自动补全内容）"
            print(f"      🔧 反思修正：补全 content")
        
        # 表达式错误 → 简化表达式
        elif tool == "calculator":
            expr = str(args.get("expression", ""))
            cleaned = re.sub(r"[^\d\.\+\-\*\/\(\)\s]", "", expr).strip()
            args["expression"] = cleaned or "1+1"
            print(f"      🔧 反思修正：表达式改为 {args['expression']}")
        
        else:
            print(f"      🔧 反思修正：保持原步骤重试")
        
        return fixed


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
        if "全流程执行日志" in prompt:
            return self._mock_summary(prompt)
        return f"[模拟生成] {prompt[:60]}..."

    def _mock_summary(self, prompt: str) -> str:
        part = prompt.split("全流程执行日志", 1)[1]
        log = part.split("本次任务失败步骤数", 1)[0].strip()
        fail = "失败步骤数：0" if "false" not in log.lower() else "存在失败步骤"
        return (f"整体执行概况：多步骤流程已执行完毕（{fail}）。\n\n"
                f"分步结果：\n{log[:700]}\n\n"
                f"最终结论：所有可执行步骤均已完成；失败步骤已在日志中标注原因。")


# ======================================================================
# StableMultiToolAgent
# ======================================================================

class StableMultiToolAgent:
    """具备自主纠错重试能力的稳定Agent"""
    
    def __init__(self):
        self.history: List[Dict] = []
        self.max_iter = 5      # 最大任务步骤数
        self.max_retry = 2     # 最大纠错重试次数
        self.llm = LLMClient()
    
    def load_history(self, history_list: List[Dict]):
        self.history = compress_history(history_list or [])
    
    def build_planning_prompt(self) -> str:
        tools_desc = tool_manager.get_tools_description()
        return f"""你是具备任务规划、多工具协同、错误自查能力的稳定AI Agent。
可用工具如下：
{tools_desc}

规则：
1. 复杂任务自主拆解为有序子任务，按顺序依赖执行
2. 精准判断每一步是否需要工具、工具名称、入参
3. 输出规范JSON任务计划，禁止多余解释
4. 遇到参数缺失、路径不明确时，自动补全合理默认值

多步骤输出格式：
{{"need_multi_step": true, "task_steps": [{{"step":1,"desc":"","tool_call":true,"tool_name":"","tool_args":{{}}}}]}}

单步骤直接输出工具调用JSON或自然语言答案。"""
    
    def build_retry_prompt(self, step: Dict, error_msg: str) -> str:
        return f"""当前执行子任务失败，请自主反思错误并修正参数重试。
任务步骤：{json.dumps(step, ensure_ascii=False)}
执行报错信息：{error_msg}

请分析错误原因，修正参数、路径、表达式或逻辑，输出修正后的完整步骤JSON，
严格保持格式不变，只修改错误内容，无需多余解释。"""
    
    def plan_task(self, user_input: str) -> Dict[str, Any]:
        if USE_MOCK or not self.llm.client:
            return MockPlanner.plan(user_input)
        context = f"历史上下文：{build_context(self.history)}\n" if self.history else ""
        prompt = f"{self.build_planning_prompt()}\n{context}用户任务：{user_input}"
        content = self.llm.chat(prompt).strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"need_multi_step": False, "content": content}
    
    @staticmethod
    def _is_business_error(result: str) -> bool:
        """业务级错误检测"""
        markers = ["失败", "错误", "未找到工具", "No such file", "不存在"]
        return any(m in result for m in markers)
    
    def execute_step_with_retry(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """单步执行 + 自动校验 + 反思修正 + 重试"""
        current_step = step
        error_log: List[str] = []
        
        for attempt in range(self.max_retry + 1):
            try:
                if not current_step.get("tool_call"):
                    return {"success": True, "result": current_step.get("desc", ""),
                            "error": "", "retried": len(error_log) > 0}
                
                tool_name = current_step.get("tool_name")
                tool_args = current_step.get("tool_args", {})
                result = tool_manager.execute_tool(tool_name, tool_args)
                
                # 2. 校验：业务级错误
                if self._is_business_error(result):
                    raise Exception(result)
                
                return {"success": True, "result": result, "error": "",
                        "retried": len(error_log) > 0}
            
            except Exception as e:
                err_msg = str(e)
                error_log.append(f"第{attempt+1}次执行失败：{err_msg}")
                print(f"      ⚠️ 第{attempt+1}次失败：{err_msg[:60]}")
                
                if attempt >= self.max_retry:
                    return {"success": False, "result": "",
                            "error": " | ".join(error_log), "retried": True}
                
                # 3+4. 反思 + 修正
                if USE_MOCK or not self.llm.client:
                    current_step = MockFixer.fix(current_step, err_msg)
                else:
                    retry_prompt = self.build_retry_prompt(current_step, err_msg)
                    content = self.llm.chat(retry_prompt)
                    try:
                        current_step = json.loads(content)
                    except json.JSONDecodeError:
                        pass
        
        return {"success": False, "result": "", "error": "重试次数耗尽，执行失败",
                "retried": True}
    
    def iterate_execute(self, task_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = task_plan.get("task_steps", [])
        execute_log: List[Dict[str, Any]] = []
        context = ""
        
        for step in steps[:self.max_iter]:
            # 写文件时继承上一步结果
            if step.get("tool_name") == "write_file" and not step.get("tool_args", {}).get("content"):
                step = json.loads(json.dumps(step))
                step["tool_args"]["content"] = context
            
            print(f"   ▶ 步骤{step.get('step')}：{step.get('desc')}")
            res = self.execute_step_with_retry(step)
            execute_log.append({
                "step": step.get("step"),
                "step_desc": step.get("desc"),
                "tool_name": step.get("tool_name", "无"),
                "success": res["success"],
                "result": res["result"],
                "error": res["error"],
                "retried": res.get("retried", False),
            })
            if res["success"]:
                context = res["result"]
                print(f"      ✅ 完成：{str(res['result'])[:60]}")
            else:
                print(f"      ❌ 放弃：{res['error'][:80]}")
        
        return execute_log
    
    def summary_result(self, user_input: str, execute_log: List[Dict]) -> str:
        fail_count = sum(1 for item in execute_log if not item["success"])
        log_json = json.dumps(execute_log, ensure_ascii=False, indent=2)
        if USE_MOCK or not self.llm.client:
            return self.llm.chat(f"用户任务：{user_input}\n全流程执行日志\n{log_json}\n"
                                 f"本次任务失败步骤数：{fail_count}")
        return self.llm.chat(f"""用户任务：{user_input}
全流程执行日志：
{log_json}

本次任务失败步骤数：{fail_count}
请根据执行情况输出：
1. 整体执行概况
2. 每一步执行结果说明
3. 失败原因复盘（如有）
4. 最终可用结论与交付内容""")
    
    def run(self, user_input: str, history_list: List[Dict]) -> Dict[str, Any]:
        self.load_history(history_list)
        print(f"\n🤖 StableMultiToolAgent | {user_input}")
        
        task_plan = self.plan_task(user_input)
        
        if not task_plan.get("need_multi_step"):
            single = self.execute_step_with_retry(task_plan)
            log = [{
                "step": 1, "step_desc": task_plan.get("desc", user_input),
                "tool_name": task_plan.get("tool_name", "无"),
                "success": single["success"], "result": single["result"],
                "error": single["error"], "retried": single.get("retried", False),
            }]
            return {"multi_step": False, "execute_log": log,
                    "final_answer": self.summary_result(user_input, log)}
        
        execute_log = self.iterate_execute(task_plan)
        final = self.summary_result(user_input, execute_log)
        return {
            "multi_step": True,
            "step_count": len(execute_log),
            "fail_count": sum(1 for x in execute_log if not x["success"]),
            "execute_log": execute_log,
            "final_answer": final,
        }


agent = StableMultiToolAgent()
