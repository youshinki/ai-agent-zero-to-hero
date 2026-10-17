# ===== agent_core.py：多工具协同+任务规划 =====

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

class MultiToolAgent:
    def __init__(self):
        self.history = []
        # 最大迭代次数，防止死循环
        self.max_iter = 5

    def load_history(self, history_list):
        self.history = compress_history(history_list)

    def build_planning_prompt(self):
        """构建任务规划提示词，让AI自主拆分多步骤任务"""
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
    {{
      "step": 1,
      "desc": "子任务描述",
      "tool_call": true/false,
      "tool_name": "工具名",
      "tool_args": {{参数}}
    }}
  ]
}}

如果仅需单步操作，直接输出单工具调用JSON或自然语言答案。
禁止多余解释、禁止Markdown格式。
"""

    def plan_task(self, user_input):
        """自主规划任务，拆解多步骤流程"""
        context = ""
        if self.history:
            context = f"历史对话上下文：{self.history}\n"

        prompt = f"{self.build_planning_prompt()}\n{context}用户最终任务：{user_input}"
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        content = res.choices[0].message.content.strip()

        try:
            plan = json.loads(content)
            return plan
        except json.JSONDecodeError:
            # 无法拆解多步骤，默认单步任务
            return {"need_multi_step": False, "content": content}

    def execute_single_step(self, step):
        """执行单步子任务"""
        if not step.get("tool_call"):
            # 无需工具，直接返回内容
            return step.get("desc", "无执行内容")
        
        # 执行工具调用
        tool_name = step.get("tool_name")
        tool_args = step.get("tool_args", {})
        return tool_manager.execute_tool(tool_name, tool_args)

    def iterate_execute(self, task_plan):
        """循环迭代执行多步骤任务"""
        steps = task_plan.get("task_steps", [])
        execute_log = []

        for idx, step in enumerate(steps[:self.max_iter]):
            step_res = self.execute_single_step(step)
            execute_log.append({
                "step": step["step"],
                "step_desc": step["desc"],
                "tool_name": step.get("tool_name", "无"),
                "result": step_res
            })
        
        return execute_log

    def summary_result(self, user_input, execute_log):
        """汇总多步骤执行结果，生成最终答案"""
        prompt = f"""用户任务：{user_input}
任务分步执行日志：
{json.dumps(execute_log, ensure_ascii=False, indent=2)}

请基于以上完整执行流程，整理出清晰、完整、结构化的最终回答，
梳理每一步操作、核心结果、最终结论，输出用户可直接使用的交付内容。
"""
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content.strip()

    def run(self, user_input, history_list):
        self.load_history(history_list)
        # 1. 自主任务规划
        task_plan = self.plan_task(user_input)

        # 单步任务兼容原有逻辑
        if not task_plan.get("need_multi_step"):
            try:
                # 尝试解析单工具调用
                if task_plan.get("tool_call"):
                    tool_res = self.execute_single_step(task_plan)
                    final_ans = self.summary_result(user_input, [task_plan])
                    return {
                        "multi_step": False,
                        "final_answer": final_ans
                    }
            except:
                return {
                    "multi_step": False,
                    "final_answer": task_plan.get("content", task_plan)
                }
        
        # 2. 多步骤任务迭代执行
        execute_log = self.iterate_execute(task_plan)
        # 3. 汇总生成最终交付
        final_answer = self.summary_result(user_input, execute_log)

        return {
            "multi_step": True,
            "step_count": len(execute_log),
            "execute_log": execute_log,
            "final_answer": final_answer
        }

# 全局实例化
agent = MultiToolAgent()
