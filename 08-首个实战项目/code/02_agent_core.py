from openai import OpenAI
from config import MODEL_API_KEY, MODEL_BASE_URL, MODEL_NAME

client = OpenAI(
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL
)

class BaseAgent:
    def __init__(self):
        self.history = []

    # 1. 思维规划：CoT分步拆解
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

    # 2. 任务执行：生成原始结果
    def execute_task(self, user_input, plan_result):
        prompt = f"""
根据任务规划结果，完整落地执行用户需求：
用户需求：{user_input}
任务规划：{plan_result}

请输出完整、清晰、可直接使用的最终内容。
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content

    # 3. 自我反思纠错：Reflexion校验优化
    def reflect_task(self, user_input, raw_result):
        prompt = f"""
你是严格的内容审核师，请自查本次输出：
用户需求：{user_input}
原始输出：{raw_result}

从以下维度自查：
1. 是否答非所问
2. 是否内容残缺、逻辑漏洞
3. 是否存在幻觉、虚假信息
4. 是否可以优化结构、措辞、完整性

输出：问题清单 + 优化后的最终成品
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content

    # Agent完整运行闭环
    def run(self, user_task):
        print("【1/3】任务规划中...")
        plan = self.plan_task(user_task)

        print("【2/3】任务执行中...")
        raw_result = self.execute_task(user_task, plan)

        print("【3/3】自我反思优化中...")
        final_result = self.reflect_task(user_task, raw_result)

        return final_result
