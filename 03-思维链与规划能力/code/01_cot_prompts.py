# 第3篇配套代码：思维链与规划能力
# 展示 CoT / ToT / ReAct / Reflexion 四种规划范式
# 运行：python 01_cot_prompts.py

# ========== 1. 普通Prompt（无思维链） ==========
def naive_prompt():
    return """
帮我分析这个问题：自媒体新人如何快速起号，直接给出答案。
"""

# ========== 2. CoT思维链Prompt ==========
def cot_prompt():
    return """
你是一个专业的自媒体运营分析师。
请你一步步思考、分步推导，再给出最终完整方案：
1. 先分析新人起号的核心难点
2. 再拆解起号的关键核心要素
3. 然后给出分阶段执行步骤
4. 最后总结避坑要点和落地建议

问题：自媒体新人如何快速起号？
"""

# ========== 3. ToT思维树（多路径探索） ==========
def tot_reasoning(problem):
    paths = [
        {"name": "方案A-低成本内容", "feasibility": 0.8, "cost": "低"},
        {"name": "方案B-投流推广", "feasibility": 0.6, "cost": "高"},
        {"name": "方案C-矩阵运营", "feasibility": 0.7, "cost": "中"}
    ]
    best = max(paths, key=lambda p: p["feasibility"])
    return f"推荐方案：{best['name']}（可行性{best['feasibility']}，成本{best['cost']}）"

# ========== 4. ReAct循环（思考-行动-观察） ==========
class ReActAgent:
    def __init__(self):
        self.history = []

    def think(self, task):
        thought = f"思考：要完成'{task}'，需要先收集信息"
        self.history.append(thought)
        return thought

    def act(self, thought):
        action = f"行动：执行搜索获取相关资料"
        self.history.append(action)
        return {"action": "search", "result": "找到3篇相关文章"}

    def observe(self, result):
        observation = f"观察：获取到{result['result']}"
        self.history.append(observation)
        return observation

    def react_loop(self, task, max_steps=3):
        print(f"🔄 ReAct循环 | 任务：{task}")
        for i in range(max_steps):
            thought = self.think(task)
            print(f"  Step{i+1}：{thought}")
            result_obj = self.act(thought)
            obs = self.observe(result_obj)
            print(f"  → {obs}")
            if "完成" in obs:
                print("  ✅ 任务完成！")
                break

# ========== 5. Reflexion反思规划 ==========
class ReflexionAgent:
    def execute(self, task):
        return f"[执行结果] 初步完成{task}"

    def reflect(self, task, result):
        issues = ["细节不够完善", "缺少数据支撑"]
        return issues

    def improve(self, task, result, issues):
        return f"[改进版] 基于{len(issues)}个问题优化后的{task}结果"

    def run(self, task):
        print(f"🔄 Reflexion循环 | 任务：{task}")
        result = self.execute(task)
        print(f"  执行：{result}")
        issues = self.reflect(task, result)
        print(f"  反思发现{len(issues)}个问题：{issues}")
        final = self.improve(task, result, issues)
        print(f"  优化后：{final}")
        return final

if __name__ == "__main__":
    print("=" * 50)
    print("1️⃣ CoT思维链对比")
    print("=" * 50)
    print("普通Prompt：", naive_prompt())
    print("CoT Prompt：", cot_prompt())

    print("\n" + "=" * 50)
    print("2️⃣ ToT思维树 - 多路径择优")
    print("=" * 50)
    print(tot_reasoning("如何提升自媒体阅读量"))

    print("\n" + "=" * 50)
    print("3️⃣ ReAct循环 - 推理+行动交替")
    print("=" * 50)
    agent = ReActAgent()
    agent.react_loop("调研竞品动态")

    print("\n" + "=" * 50)
    print("4️⃣ Reflexion反思 - 执行→反思→改进")
    print("=" * 50)
    ref = ReflexionAgent()
    ref.run("生成市场分析报告")
