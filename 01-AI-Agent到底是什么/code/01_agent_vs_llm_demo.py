# 第1篇配套代码：AI Agent到底是什么？
# 展示普通大模型 vs AI Agent 的本质区别
# 运行：python 01_agent_vs_llm_demo.py

# ========== 1. 普通大模型对话（被动问答） ==========
def simple_chat(user_input):
    """模拟普通大模型对话 - 只能被动回答"""
    print(f"用户：{user_input}")
    print("AI：这是一个被动回答...")
    return "这是单次问答结果"

# ========== 2. AI Agent 核心执行流程（主动干活） ==========
class SimpleAgent:
    """模拟AI Agent - 能主动规划、执行、反思"""
    
    def __init__(self):
        self.memory = []
        self.tasks = []
    
    def perceive(self, goal):
        """感知输入 - 理解用户目标"""
        return f"理解目标：{goal}"
    
    def plan(self, goal):
        """任务规划 - 拆解复杂任务"""
        steps = [
            f"步骤1：分析{goal}的核心需求",
            "步骤2：收集必要信息",
            "步骤3：分步执行",
            "步骤4：检查结果质量",
            "步骤5：输出最终结果"
        ]
        return steps
    
    def execute(self, step):
        """执行任务"""
        return f"执行：{step}"
    
    def reflect(self, result):
        """自我反思"""
        issues = []
        if len(result) < 10:
            issues.append("结果不够详细")
        return issues
    
    def run(self, goal):
        print(f"\n🎯 Agent接收目标：{goal}")
        print("1️⃣ 感知输入...")
        self.perceive(goal)
        print("2️⃣ 任务规划...")
        steps = self.plan(goal)
        for s in steps:
            print(f"   {s}")
        print("3️⃣ 分步执行...")
        for s in steps[:2]:
            result = self.execute(s)
            print(f"   ✅ {result}")
        print("4️⃣ 自我反思...")
        issues = self.reflect(result)
        if issues:
            print(f"   ⚠️ 发现{len(issues)}个问题，正在优化...")
        print("5️⃣ 输出最终结果")
        print("🏁 Agent自主完成任务！")

if __name__ == "__main__":
    print("=" * 50)
    print("普通大模型模式：一问一答，被动响应")
    print("=" * 50)
    simple_chat("帮我整理本周工作内容并生成周报")
    
    print("\n" + "=" * 50)
    print("AI Agent模式：目标驱动，自主执行")
    print("=" * 50)
    agent = SimpleAgent()
    agent.run("帮我整理本周工作内容，生成周报，标注未完成任务，给出下周计划")
