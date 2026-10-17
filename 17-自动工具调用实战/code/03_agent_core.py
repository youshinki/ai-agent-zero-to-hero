# ===== agent_core.py：自主判断是否调用工具 =====

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

class ToolAgent:
    def __init__(self):
        self.history = []

    def load_history(self, history_list):
        self.history = compress_history(history_list)

    def build_system_prompt(self):
        return """你是一个具备自动工具调用能力的AI Agent。
请根据用户任务自主判断：
1. 是否需要调用工具；
2. 需要调用哪个工具；
3. 需要传入什么参数。

如果你认为不需要调用工具，请直接给出自然语言回答。
如果你认为需要调用工具，请严格返回以下JSON格式：
{
  "tool_call": true,
  "tool_name": "工具名称",
  "tool_args": {
    "参数名": "参数值"
  }
}

不要在JSON外添加多余解释。
"""

    def decide_tool(self, user_input):
        """让Agent自主决定是否调用工具"""
        tools_desc = tool_manager.get_tools_description()
        system_prompt = self.build_system_prompt()

        context = ""
        if self.history:
            context = f"历史对话：{self.history}\n"

        prompt = f"{system_prompt}\n\n{tools_desc}\n\n{context}用户任务：{user_input}"

        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )

        content = res.choices[0].message.content.strip()

        try:
            decision = json.loads(content)
            if decision.get("tool_call"):
                return decision
        except json.JSONDecodeError:
            pass

        return {"tool_call": False, "answer": content}

    def execute_tool_call(self, decision):
        """执行真实工具调用"""
        tool_name = decision["tool_name"]
        tool_args = decision["tool_args"]
        return tool_manager.execute_tool(tool_name, tool_args)

    def reflect_tool_result(self, user_input, tool_result):
        """根据工具结果继续分析，生成最终答案"""
        prompt = f"""用户任务：{user_input}

工具执行结果：
{tool_result}

请根据工具结果，给用户一个清晰、完整的最终回答。
"""
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content

    def run(self, user_input, history_list):
        self.load_history(history_list)
        decision = self.decide_tool(user_input)

        if decision.get("tool_call"):
            tool_result = self.execute_tool_call(decision)
            final_answer = self.reflect_tool_result(user_input, tool_result)
            return {
                "tool_call": True,
                "tool_name": decision["tool_name"],
                "tool_args": decision["tool_args"],
                "tool_result": tool_result,
                "final_answer": final_answer
            }
        else:
            return {
                "tool_call": False,
                "final_answer": decision["answer"]
            }

agent = ToolAgent()
