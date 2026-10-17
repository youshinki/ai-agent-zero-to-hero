from openai import OpenAI
from config import MODEL_API_KEY, MODEL_BASE_URL, MODEL_NAME
from tool_core import TOOLS_DEFINITION, execute_tool

client = OpenAI(
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL
)

class OfficeAgent:
    def __init__(self):
        self.history = []
        self.knowledge_context = ""

    # 注入RAG检索结果
    def set_knowledge(self, context):
        self.knowledge_context = context

    # 1. 工具调用决策：判断是否需要调用工具
    def decide_and_execute_tool(self, user_input):
        messages = [
            {"role": "system", "content": "你是一个智能办公助手，可以调用工具完成任务。请根据用户需求判断是否需要调用工具。"},
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS_DEFINITION,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # 如果模型决定调用工具
        if message.tool_calls:
            tool_results = []
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = eval(tool_call.function.arguments)  # 解析参数JSON

                print(f"  🛠 调用工具：{tool_name}")
                result = execute_tool(tool_name, tool_args)
                tool_results.append(f"【{tool_name}】\n{result}")

            return "\n\n".join(tool_results)
        else:
            # 不需要工具，返回None
            return None

    # 2. 任务执行：结合工具结果+知识库生成答案
    def execute_task(self, user_input, tool_result):
        knowledge_part = f"\n参考资料：{self.knowledge_context}" if self.knowledge_context else ""
        tool_part = f"\n工具执行结果：{tool_result}" if tool_result else ""

        prompt = f"""
用户需求：{user_input}
{tool_part}
{knowledge_part}

请基于以上信息，完整、准确地回答用户问题。
如果工具结果中包含错误信息，请如实告知用户。
        """

        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content

    # 3. 自我反思纠错（复用之前逻辑）
    def reflect_task(self, user_input, raw_result):
        prompt = f"""
你是内容审核师，请自查本次回答：
用户需求：{user_input}
原始输出：{raw_result}

自查维度：
1. 是否准确回答了用户问题
2. 是否存在幻觉或编造内容
3. 工具结果是否被正确使用
4. 逻辑是否通顺、表达是否清晰

输出：问题清单 + 优化后的最终答案
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content

    # Agent完整运行闭环
    def run(self, user_task):
        print("【1/3】判断是否需要调用工具...")
        tool_result = self.decide_and_execute_tool(user_task)

        print("【2/3】结合工具结果生成答案...")
        raw_result = self.execute_task(user_task, tool_result)

        print("【3/3】反思优化纠错...")
        final_result = self.reflect_task(user_task, raw_result)

        return final_result
