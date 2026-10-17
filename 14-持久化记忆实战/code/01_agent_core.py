# ===== agent_core.py 升级：多轮上下文记忆 =====

from openai import OpenAI
from config import MODEL_API_KEY, MODEL_BASE_URL, MODEL_NAME
client = OpenAI(
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL
)
class BaseAgent:
    def __init__(self):
        self.history = []
    # 载入历史对话
    def load_history(self, history_list):
        self.history = history_list
    # 任务规划（带上下文）
    def plan_task(self, user_input):
        context = ""
        if self.history:
            context = f"历史对话记录：{self.history}\n"
        prompt = f"""
你是专业AI任务规划师，请结合历史对话，分步思考用户当前任务。
{context}
当前用户新需求：{user_input}
请严格输出：
1. 任务核心目标
2. 结合上下文的任务拆解步骤
3. 本次执行注意事项
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content
    # 任务执行（带上下文）
    def execute_task(self, user_input, plan_result):
        context = ""
        if self.history:
            context = f"历史对话记录：{self.history}\n"
        prompt = f"""
结合历史对话与任务规划，完整落地执行：
{context}
当前需求：{user_input}
任务规划：{plan_result}
输出完整、连贯、贴合上下文的最终内容。
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content
    # 自我反思（带上下文校验）
    def reflect_task(self, user_input, raw_result):
        context = ""
        if self.history:
            context = f"历史对话记录：{self.history}\n"
        prompt = f"""
结合历史对话自查本次回答是否连贯、合理：
{context}
当前需求：{user_input}
原始输出：{raw_result}
自查：连贯性、完整性、是否遗忘上文、是否逻辑冲突
输出：问题清单 + 最终优化答案
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content
    # 完整多轮对话闭环
    def run_with_history(self, user_task, history_list):
        self.load_history(history_list)
        plan = self.plan_task(user_task)
        raw = self.execute_task(user_task, plan)
        final = self.reflect_task(user_task, raw)
        return {
            "user_task": user_task,
            "plan": plan,
            "raw_result": raw,
            "final_result": final
        }
agent = BaseAgent()
