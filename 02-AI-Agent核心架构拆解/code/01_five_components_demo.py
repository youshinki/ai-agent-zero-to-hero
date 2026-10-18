# 第2篇配套代码：AI Agent核心架构拆解
# 展示五大基础组件的协作关系
# 运行：python 01_five_components_demo.py

import json
from datetime import datetime

# ========== Agent五大核心组件 ==========

class LLMBrain:
    """组件1：大脑 - 大模型核心推理引擎"""
    def think(self, prompt):
        # 实际项目中调用 OpenAI / DeepSeek 等 API
        return f"[大脑思考] 基于'{prompt}'生成推理结果"

class MemoryModule:
    """组件2：记忆模块 - 存储和检索历史信息"""
    def __init__(self):
        self.short_term = []
        self.long_term = {}
    
    def remember(self, key, value):
        self.long_term[key] = {
            "value": value,
            "time": datetime.now().isoformat()
        }
    
    def recall(self, key):
        return self.long_term.get(key)
    
    def add_context(self, msg):
        self.short_term.append(msg)

class PlanningModule:
    """组件3：规划模块 - 任务拆解与调度"""
    def decompose(self, goal):
        steps = [
            {"step": 1, "action": "信息收集", "status": "pending"},
            {"step": 2, "action": "数据分析", "status": "pending"},
            {"step": 3, "action": "内容生成", "status": "pending"},
            {"step": 4, "action": "质量检查", "status": "pending"}
        ]
        return steps

class ToolModule:
    """组件4：工具模块 - 调用外部能力"""
    def __init__(self):
        self.tools = {
            "web_search": "搜索互联网信息",
            "calculator": "数学计算",
            "read_file": "读取本地文件"
        }
    
    def call(self, tool_name, params):
        if tool_name == "calculator":
            return f"[计算结果] {eval(params['expression'])}"
        return f"[工具结果] 使用{tool_name}执行完成"

class ReflectionModule:
    """组件5：反思模块 - 自我检查与纠错"""
    def check(self, result):
        issues = []
        if "错误" in result or "幻觉" in result:
            issues.append("检测到可能的不准确信息")
        return issues
    
    def optimize(self, result, issues):
        if issues:
            return result + "\n[已根据反思结果优化]"
        return result

# ========== 完整Agent系统 ==========
class CompleteAgent:
    def __init__(self):
        self.brain = LLMBrain()
        self.memory = MemoryModule()
        self.planner = PlanningModule()
        self.tools = ToolModule()
        self.reflector = ReflectionModule()
    
    def run(self, user_goal):
        print(f"🤖 Agent启动 | 目标：{user_goal}")
        
        # 1. 记忆调取
        print("\n📝 [记忆模块] 检索历史相关记忆...")
        past = self.memory.recall("user_preference")
        print(f"   找到历史记忆：{past}")
        
        # 2. 任务规划
        print("\n📋 [规划模块] 任务拆解...")
        steps = self.planner.decompose(user_goal)
        for s in steps:
            print(f"   - 步骤{s['step']}：{s['action']}")
        
        # 3. 工具执行
        print("\n🔧 [工具模块] 调用外部工具...")
        result = self.tools.call("calculator", {"expression": "100*0.3"})
        print(f"   工具执行结果：{result}")
        
        # 4. 大脑思考
        print("\n🧠 [大脑模块] 整合信息生成内容...")
        output = self.brain.think(f"{user_goal} + 工具结果：{result}")
        
        # 5. 反思优化
        print("\n🔄 [反思模块] 自我检查...")
        issues = self.reflector.check(output)
        final = self.reflector.optimize(output, issues)
        
        # 6. 记忆留存
        print("\n💾 [记忆模块] 保存本次经验...")
        self.memory.remember("last_task", user_goal)
        
        print(f"\n✅ 最终输出：{final}")
        return final

if __name__ == "__main__":
    print("=" * 60)
    print("AI Agent 五大核心组件协同演示")
    print("LLMBrain + MemoryModule + PlanningModule + ToolModule + ReflectionModule")
    print("=" * 60)
    agent = CompleteAgent()
    agent.run("帮我计算本月预算并生成报告")
