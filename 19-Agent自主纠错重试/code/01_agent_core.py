# ===== agent_core.py：容错纠错重试完整版 =====

from openai import OpenAI
from config import MODEL_API_KEY, MODEL_BASE_URL, MODEL_NAME
from memory_utils import compress_history
from tools.tool_manager import create_default_tools
import json

client = OpenAI(
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL
)

tool_manager = create_default_tools()

class StableMultiToolAgent:
    def __init__(self):
        self.history = []
        self.max_iter = 5        # 最大任务步骤数
        self.max_retry = 2       # 最大纠错重试次数

    def load_history(self, history_list):
        self.history = compress_history(history_list)

    # 任务规划提示词
    def build_planning_prompt(self):
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
{{
  "need_multi_step": true,
  "task_steps": [{{"step":1,"desc":"","tool_call":true,"tool_name":"","tool_args":{{}}}}]
}}

单步骤直接输出工具调用JSON或自然语言答案。
"""

    # 错误反思修正提示词
    def build_retry_prompt(self, step, error_msg):
        return f"""当前执行子任务失败，请自主反思错误并修正参数重试。
任务步骤：{step}
执行报错信息：{error_msg}

请分析错误原因，修正参数、路径、表达式或逻辑，输出修正后的完整步骤JSON，
严格保持格式不变，只修改错误内容，无需多余解释。
"""

    # 任务整体规划
    def plan_task(self, user_input):
        context = f"历史上下文：{self.history}\n" if self.history else ""
        prompt = f"{self.build_planning_prompt()}\n{context}用户任务：{user_input}"

        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        content = res.choices[0].message.content.strip()

        try:
            return json.loads(content)
        except:
            return {"need_multi_step": False, "content": content}

    # 单步执行 + 自动重试
    def execute_step_with_retry(self, step):
        current_step = step
        error_log = []

        for i in range(self.max_retry + 1):
            try:
                if not current_step.get("tool_call"):
                    return {"success": True, "result": current_step.get("desc", ""), "error": ""}

                # 执行工具调用
                tool_name = current_step.get("tool_name")
                tool_args = current_step.get("tool_args", {})
                result = tool_manager.execute_tool(tool_name, tool_args)

                # 检测业务级错误
                if "失败" in result or "错误" in result or "未找到工具" in result:
                    raise Exception(result)

                return {"success": True, "result": result, "error": ""}

            except Exception as e:
                err_msg = str(e)
                error_log.append(f"第{i+1}次执行失败：{err_msg}")

                # 重试次数耗尽，直接返回失败
                if i >= self.max_retry:
                    return {"success": False, "result": "", "error": " | ".join(error_log)}

                # AI 自主反思修正参数
                retry_prompt = self.build_retry_prompt(current_step, err_msg)
                retry_res = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": retry_prompt}]
                )
                try:
                    current_step = json.loads(retry_res.choices[0].message.content.strip())
                except:
                    # 修正格式失败，维持原步骤重试
                    pass

        return {"success": False, "result": "", "error": "重试次数耗尽，执行失败"}

    # 批量迭代执行所有步骤
    def iterate_execute(self, task_plan):
        steps = task_plan.get("task_steps", [])
        execute_log = []

        for step in steps[:self.max_iter]:
            res = self.execute_step_with_retry(step)
            execute_log.append({
                "step": step["step"],
                "step_desc": step["desc"],
                "tool_name": step.get("tool_name", "无"),
                "success": res["success"],
                "result": res["result"],
                "error": res["error"]
            })
        return execute_log

    # 汇总最终结果
    def summary_result(self, user_input, execute_log):
        fail_count = sum(1 for item in execute_log if not item["success"])
        prompt = f"""用户任务：{user_input}
全流程执行日志：
{json.dumps(execute_log, ensure_ascii=False, indent=2)}

本次任务失败步骤数：{fail_count}
请根据执行情况输出：
1. 整体执行概况
2. 每一步执行结果说明
3. 失败原因复盘（如有）
4. 最终可用结论与交付内容
"""
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content.strip()

    # 总入口
    def run(self, user_input, history_list):
        self.load_history(history_list)
        task_plan = self.plan_task(user_input)

        # 单步任务
        if not task_plan.get("need_multi_step"):
            try:
                if task_plan.get("tool_call"):
                    res = self.execute_step_with_retry(task_plan)
                    final_ans = self.summary_result(user_input, [res])
                    return {
                        "multi_step": False,
                        "final_answer": final_ans
                    }
            except:
                return {
                    "multi_step": False,
                    "final_answer": task_plan.get("content", "任务执行异常，请重试")
                }

        # 多步任务
        execute_log = self.iterate_execute(task_plan)
        final_answer = self.summary_result(user_input, execute_log)

        return {
            "multi_step": True,
            "step_count": len(execute_log),
            "fail_count": sum(1 for x in execute_log if not x["success"]),
            "execute_log": execute_log,
            "final_answer": final_answer
        }

agent = StableMultiToolAgent()
