# 第6篇配套代码：Agent反射与自我纠错
# Reflexion机制：执行→反思→改进→执行循环
# 运行：python 01_reflexion_agent.py

import json

# ========== 模拟大模型调用 ==========
def llm_call(prompt):
    """模拟大模型API调用"""
    # 实际使用替换为 openai / deepseek 等真实调用
    return f"模型原始输出：针对「{prompt[:50]}...」的初步分析结果"

# ========== 1. 基础反射三步法 ==========
class ReflexionAgent:
    """Reflexion反射机制Agent"""
    
    def __init__(self, max_iterations=3):
        self.max_iterations = max_iterations
        self.history = []
    
    def execute(self, user_input):
        """第一轮：常规任务执行"""
        base_prompt = f"""请完成用户任务：
任务：{user_input}
要求：输出完整、可落地的结果"""
        result = llm_call(base_prompt)
        self.history.append({"stage": "execute", "result": result})
        return result
    
    def reflect(self, user_input, raw_result):
        """第二轮：反射自查纠错"""
        reflect_prompt = f"""
你是严格的任务审核专家，请按以下维度逐条自查：

用户需求：{user_input}
原始输出：{raw_result}

自查维度：
1. 是否存在事实幻觉、虚假信息
2. 是否答非所问、内容残缺
3. 逻辑是否矛盾、有无漏洞
4. 格式是否规范、是否需要优化
5. 用户需求是否全部覆盖

请输出JSON格式的纠错报告：
{{
    "issues": ["问题1", "问题2"],
    "severity": "high/medium/low",
    "improvement_suggestions": ["改进1", "改进2"]
}}
"""
        result = llm_call(reflect_prompt)
        self.history.append({"stage": "reflect", "result": result})
        return result
    
    def optimize(self, user_input, raw_result, reflect_report):
        """第三轮：迭代优化"""
        optimize_prompt = f"""
根据自查报告优化输出，交付最终高质量结果：

需求：{user_input}
当前结果：{raw_result}
审核报告：{reflect_report}

要求：
1. 修正所有发现的问题
2. 保持专业性和完整度
3. 输出可直接使用的最终版本
"""
        result = llm_call(optimize_prompt)
        self.history.append({"stage": "optimize", "result": result})
        return result
    
    def run(self, user_input):
        """完整纠错流程"""
        print(f"🎯 用户需求：{user_input}")
        print("\n1️⃣ [执行阶段] 生成初始结果...")
        raw = self.execute(user_input)
        print(f"   原始输出：{raw}")
        
        print("\n2️⃣ [反思阶段] 自我检查...")
        reflect_result = self.reflect(user_input, raw)
        print(f"   反思发现：{reflect_result}")
        
        print("\n3️⃣ [优化阶段] 迭代改进...")
        final = self.optimize(user_input, raw, reflect_result)
        print(f"   最终结果：{final}")
        
        print(f"\n✅ 经过{len(self.history)}轮处理完成")
        return final

# ========== 2. 多层反射检查器 ==========
class MultiLayerReflector:
    """多层反射检查"""
    
    @staticmethod
    def result_layer_check(result, requirements):
        """结果层检查"""
        checks = []
        for req in requirements:
            if req in result:
                checks.append({"requirement": req, "passed": True})
            else:
                checks.append({"requirement": req, "passed": False})
        return checks
    
    @staticmethod
    def process_layer_check(steps_taken, expected_steps):
        """过程层检查"""
        missing = [s for s in expected_steps if s not in steps_taken]
        return {
            "completed_steps": len(steps_taken),
            "missing_steps": missing,
            "is_complete": len(missing) == 0
        }
    
    @staticmethod
    def experience_layer_check(this_result, past_mistakes):
        """经验层检查"""
        repeated_errors = []
        for mistake in past_mistakes:
            if mistake["pattern"] in this_result:
                repeated_errors.append(mistake["pattern"])
        return {
            "repeated_errors": repeated_errors,
            "is_learning": len(repeated_errors) == 0
        }

# ========== 3. 带纠错的Agent ==========
class RobustAgent:
    """带自主纠错的Robust Agent"""
    
    def __init__(self):
        self.past_mistakes = []  # 记录历史错误模式
    
    def run_with_retry(self, task, max_retries=3):
        """带重试的执行"""
        for attempt in range(1, max_retries + 1):
            print(f"\n  🔄 第{attempt}次尝试...")
            result = llm_call(f"第{attempt}次执行：{task}")
            
            # 检查质量
            if "错误" not in result and "不知道" not in result:
                return result
            else:
                print(f"  ⚠️ 检测到问题，准备重试...")
        
        return "经过多次尝试后，建议人工介入"

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 Agent反射与自我纠错")
    print("Reflexion机制：执行→反思→改进→执行")
    print("=" * 60)
    
    # 1. 基础反射流程
    print("\n1️⃣ 基础反射三步法")
    print("-" * 40)
    agent = ReflexionAgent()
    result = agent.run("分析2024年AI Agent行业发展趋势")
    
    # 2. 多层检查
    print("\n2️⃣ 多层反射检查")
    print("-" * 40)
    checker = MultiLayerReflector()
    
    result_layer = checker.result_layer_check(
        "AI Agent趋势分析报告",
        ["AI Agent", "发展趋势", "2024"]
    )
    print("结果层检查：")
    for c in result_layer:
        status = "✅" if c["passed"] else "❌"
        print(f"  {status} {c['requirement']}")
    
    process_check = checker.process_layer_check(
        ["收集数据", "分析趋势", "生成报告"],
        ["收集数据", "分析趋势", "生成报告", "质量检查"]
    )
    print(f"\n过程层检查：")
    print(f"  进度：{process_check['completed_steps']}/{len(process_check['missing_steps']) + process_check['completed_steps']}")
    
    # 3. Robust Agent
    print("\n3️⃣ 带重试的Robust Agent")
    print("-" * 40)
    robust = RobustAgent()
    final = robust.run_with_retry("生成复杂分析报告")
    print(f"  最终结果：{final}")
