from openai import OpenAI
from config import MODEL_API_KEY, MODEL_BASE_URL, MODEL_NAME

client = OpenAI(
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL
)

class BaseAgent:
    def __init__(self):
        self.history = []
        self.knowledge_context = ""

    # 注入检索到的私有知识
    def set_knowledge(self, context):
        self.knowledge_context = context

    # 任务规划
    def plan_task(self, user_input):
        prompt = f"""
你是专业AI任务规划师，请严格分步思考、拆解用户任务：
用户需求：{user_input}

请输出：
1. 任务核心目标
2. 任务拆解步骤
3. 执行注意事项
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content

    # 融合知识库执行任务
    def execute_task(self, user_input, plan_result):
        prompt = f"""
请结合私有知识库内容，落地执行用户需求：
用户需求：{user_input}
任务规划：{plan_result}
私有参考资料：{self.knowledge_context}

严格基于参考资料回答，禁止编造、禁止幻觉、禁止脱离文档内容。
输出完整、清晰、准确的答案。
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content

    # 自我反思纠错
    def reflect_task(self, user_input, raw_result):
        prompt = f"""
你是严格的内容审核师，请自查本次基于知识库的回答：
用户需求：{user_input}
原始输出：{raw_result}

自查维度：
1. 是否脱离私有文档内容、存在幻觉编造
2. 是否答非所问、遗漏关键信息
3. 逻辑是否通顺、内容是否完整

输出：问题清单 + 优化后的最终答案
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content

    # 完整运行闭环
    def run(self, user_task):
        print("【1/3】任务规划中...")
        plan = self.plan_task(user_task)

        print("【2/3】结合知识库执行中...")
        raw_result = self.execute_task(user_task, plan)

        print("【3/3】反思优化纠错中...")
        final_result = self.reflect_task(user_task, raw_result)

        return final_result
