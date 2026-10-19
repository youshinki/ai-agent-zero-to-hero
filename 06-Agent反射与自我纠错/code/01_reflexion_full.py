#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
  第6篇配套完整演示代码
  Agent反射与自我纠错 —— Reflexion反射机制全面实现
==========================================================================

  本文件覆盖文章中全部技术点：
    ✅ 普通Agent缺陷（单向执行、无校验、无复盘、屡错不改）
    ✅ Reflexion三步法（执行→反思→优化）完整实现
    ✅ 三层反射架构（结果层、过程层、经验层）
    ✅ 反射与规划/工具/记忆/输出的联动闭环
    ✅ 无反射Agent vs 带反射Agent 效果对比
    ✅ 3个核心开发技巧

  运行方式：
    python 01_reflexion_full.py

  作者：AI Agent 零基础实战
  版本：1.0
==========================================================================
"""

import json
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, field


# ====================================================================
#  第一部分：模拟大模型调用（Mock LLM）
# ====================================================================

class MockLLM:
    """模拟大模型调用，无需真实API"""

    @staticmethod
    def call(prompt: str, role: str = "assistant") -> str:
        """模拟LLM返回，根据prompt内容生成不同质量的回复"""
        # 检测任务类型
        if "审核" in prompt or "自查" in prompt or "反思" in prompt:
            return MockLLM._reflect_response(prompt)
        elif "优化" in prompt or "修正" in prompt:
            return MockLLM._optimize_response(prompt)
        elif "规划" in prompt or "拆解" in prompt:
            return MockLLM._plan_response(prompt)
        else:
            return MockLLM._execute_response(prompt)

    @staticmethod
    def _execute_response(prompt: str) -> str:
        """模拟执行阶段回复 - 包含一些常见错误"""
        if "周报" in prompt or "总结" in prompt:
            return """本周工作完成情况：
- 项目A进展顺利
- 项目B有延迟
- 团队会议参加
下周计划继续推进。"""
        elif "分析" in prompt:
            return """根据现有数据，2024年AI Agent市场规模约100亿美元。
主要玩家有OpenAI、Google、Microsoft。
趋势是向多模态和自主决策方向发展。"""
        elif "代码" in prompt or "bug" in prompt:
            return """def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result  # 缺少空值检查"""
        elif "调研" in prompt or "报告" in prompt:
            return """竞品调研报告：
1. 竞品A：主打低端市场，价格便宜
2. 竞品B：主打高端市场，功能丰富
3. 建议：我们选择中端定位"""
        else:
            return f"针对任务的初步执行结果。包含一些可以改进的地方。"

    @staticmethod
    def _reflect_response(prompt: str) -> str:
        """模拟反思阶段的回复 - 检查问题"""
        issues = []
        improvements = []

        if "周报" in prompt or "总结" in prompt:
            issues = [
                "缺少具体数据支撑，如完成百分比、具体数字",
                "未区分重点工作和常规工作",
                "缺少风险问题和解决方案的说明",
                "格式不够规范，缺少时间维度"
            ]
            improvements = [
                "补充具体数据指标，如项目A完成80%，项目B延迟2天",
                "按优先级排列重点工作",
                "增加问题和风险板块",
                "使用标准化周报模板"
            ]
        elif "分析" in prompt:
            issues = [
                "数据来源不明确，可能过时",
                "缺少细分领域的具体分析",
                "未提及中国市场特殊情况",
                "结论过于笼统，缺少 actionable insights"
            ]
            improvements = [
                "注明数据来源和时间",
                "增加细分赛道分析",
                "补充中国市场的政策环境和本土玩家",
                "给出可执行的策略建议"
            ]
        elif "代码" in prompt:
            issues = [
                "缺少输入参数校验",
                "未处理边界情况（空列表）",
                "缺少异常处理机制",
                "代码可读性可以进一步提升"
            ]
            improvements = [
                "添加类型注解和参数校验",
                "处理空列表、None等边界情况",
                "添加try/except异常处理",
                "添加函数注释和类型提示"
            ]
        else:
            issues = ["内容完整性不足", "逻辑可以更严谨", "可以增加更多具体细节"]
            improvements = ["补充完整信息", "优化逻辑结构", "增加具体案例支撑"]

        return json.dumps({
            "found_issues": issues,
            "improvements": improvements,
            "severity": "medium",
            "overall_quality": 6.5
        }, ensure_ascii=False)

    @staticmethod
    def _optimize_response(prompt: str) -> str:
        """模拟优化后的回复"""
        if "周报" in prompt:
            return """【本周工作总结】（2024年第X周）

一、重点工作完成情况
1. 项目A - 核心功能开发（进度：80% ✅）
   - 完成用户模块开发和测试
   - 数据库优化完成，查询性能提升40%
   
2. 项目B - 客户需求跟进（进度：60% ⚠️）
   - 已完成需求分析
   - 延期原因：客户需求变更
   - 解决方案：已重新排期，预计下周完成

二、常规工作
- 参加3次团队会议
- 完成2次代码评审
- 处理5个线上问题

三、风险与问题
- 项目B延期风险，已与PM沟通调整计划
- 建议增加一名开发资源

四、下周计划
1. 完成项目A剩余功能（预计周三）
2. 启动项目B开发（预计周四）
3. 准备季度汇报材料

---
反思优化版本：补充了具体数据、分类更清晰、增加了风险板块"""
        elif "分析" in prompt:
            return """【2024年AI Agent市场分析报告】

📊 市场规模
- 全球：约100亿美元（来源：IDC 2024Q1报告）
- 中国：约25亿美元，同比增长52%
- 预计2027年全球达300亿美元

🏢 竞争格局
1. 国际巨头
   - OpenAI：GPT-4 + Assistants API，生态最完善
   - Google：Gemini + Vertex AI Agent Builder
   - Microsoft：Copilot生态 + AutoGen框架

2. 中国厂商
   - 百度：文心大模型 + 智能体平台
   - 阿里：通义千问 + 百炼平台
   - 创业公司：澜舟科技、月之暗面等

🎯 细分赛道机会
1. 企业级RAG知识库（需求最旺盛）
2. 办公自动化Agent（标准化程度高）
3. 垂直行业Agent（医疗/法律/金融）

💡 策略建议
1. 优先切入企业RAG赛道，客单价高
2. 关注开源模型降低推理成本
3. 构建行业Know-how壁垒

---
反思优化版：数据来源清晰、细分赛道具体、建议可执行"""
        elif "代码" in prompt:
            return """from typing import List, Optional, Union

def process_data(data: Optional[List[Union[int, float]]]) -> List[Union[int, float]]:
    \"\"\"
    处理数据列表，对每个元素乘以2。
    
    Args:
        data: 输入数据列表，可以为None
        
    Returns:
        处理后的数据列表
        
    Raises:
        TypeError: 输入类型不正确
    \"\"\"
    if data is None:
        return []
    
    if not isinstance(data, list):
        raise TypeError("输入必须是列表类型")
    
    result = []
    for item in data:
        if not isinstance(item, (int, float)):
            continue  # 跳过非数字类型
        result.append(item * 2)
    
    return result

# 使用示例
if __name__ == "__main__":
    print(process_data([1, 2, 3]))       # [2, 4, 6]
    print(process_data(None))             # []
    print(process_data([1, "a", 3]))      # [2, 6]

---
反思优化版：添加类型注解、异常处理、边界检查和完整文档"""
        else:
            return f"优化后的最终版本：修复了所有发现的问题，内容更加完整和准确。"

    @staticmethod
    def _plan_response(prompt: str) -> str:
        """模拟规划阶段"""
        return json.dumps({
            "goal": "理解用户需求",
            "steps": [
                "分析用户输入的核心目标",
                "拆解为可执行的子任务",
                "确定执行优先级",
                "判断是否需要调用工具",
                "分步执行",
                "检查结果质量"
            ],
            "tool_needed": "分析" in prompt or "搜索" in prompt
        }, ensure_ascii=False)


# ====================================================================
#  第二部分：反射纠错核心系统
# ====================================================================

@dataclass
class ReflectionReport:
    """反射报告数据结构"""
    found_issues: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    severity: str = "medium"
    overall_quality: float = 5.0


class ExecutionResult:
    """执行结果"""
    def __init__(self, content: str, stage: str = "initial"):
        self.content = content
        self.stage = stage
        self.issues: List[str] = []
        self.quality_score: float = 0


class ReflexionAgent:
    """
    Reflexion反射机制Agent - 完整三步法
    
    核心思路：
    1. 第一轮：正常执行任务，输出初始结果
    2. 第二轮：切换审核模式，自查纠错
    3. 第三轮：基于自查报告，迭代优化最终输出
    """
    
    def __init__(self, name: str = "ReflexionAgent"):
        self.name = name
        self.llm = MockLLM()
        self.history: List[Dict] = []
        self.execution_count = 0
    
    # ========== 第一步：任务执行 ==========
    
    def execute(self, user_input: str) -> ExecutionResult:
        """第一轮：常规任务执行"""
        self.execution_count += 1
        prompt = f"请完成用户任务：{user_input}"
        content = self.llm.call(prompt)
        
        result = ExecutionResult(content, "initial")
        self.history.append({
            "stage": "execute",
            "input": user_input,
            "output": content
        })
        return result
    
    # ========== 第二步：反射自查 ==========
    
    def reflect(self, user_input: str, raw_result: ExecutionResult) -> ReflectionReport:
        """第二轮：反射自查纠错 - 6个维度全面检查"""
        reflect_prompt = f"""
你现在是严格的任务审核专家。请自查本次任务全过程，输出JSON格式的纠错报告。

用户需求：{user_input}
原始输出：{raw_result.content}

请从以下6个维度逐条自查：
1. 是否存在事实幻觉、虚假数据、编造信息
2. 是否答非所问、内容残缺、需求未覆盖
3. 逻辑是否矛盾、有无明显漏洞
4. 格式是否规范、是否需优化
5. 安全合规：是否包含敏感信息
6. 需求覆盖度：是否完全满足用户需求

输出严格的纠错报告（JSON格式）：
- found_issues: 问题清单（至少3条）
- improvements: 改进建议（对应每个问题）
- severity: high/medium/low
- overall_quality: 1-10的评分
"""
        reflect_text = self.llm.call(reflect_prompt)
        
        try:
            report_data = json.loads(reflect_text)
            report = ReflectionReport(
                found_issues=report_data.get("found_issues", ["未发现明显问题"]),
                improvements=report_data.get("improvements", ["保持现状"]),
                severity=report_data.get("severity", "medium"),
                overall_quality=report_data.get("overall_quality", 6.0)
            )
        except json.JSONDecodeError:
            report = ReflectionReport(
                found_issues=["反思报告解析失败"],
                improvements=["重新执行"],
                severity="high",
                overall_quality=3.0
            )
        
        raw_result.issues = report.found_issues
        raw_result.quality_score = report.overall_quality
        
        self.history.append({
            "stage": "reflect",
            "issues": report.found_issues,
            "quality": report.overall_quality
        })
        
        return report
    
    # ========== 第三步：迭代优化 ==========
    
    def optimize(self, user_input: str, raw_result: ExecutionResult, 
                 report: ReflectionReport) -> ExecutionResult:
        """第三轮：基于反思报告迭代优化"""
        optimize_prompt = f"""
根据自查纠错报告，优化你的输出，交付最终高质量版本：

用户需求：{user_input}
当前版本：{raw_result.content}
发现的问题：{json.dumps(report.found_issues, ensure_ascii=False)}
改进建议：{json.dumps(report.improvements, ensure_ascii=False)}

要求：
1. 修正所有发现的问题
2. 采纳改进建议
3. 标记哪些是优化内容
4. 输出完整、可直接使用的最终版本
"""
        optimized_content = self.llm.call(optimize_prompt)
        
        final_result = ExecutionResult(optimized_content, "optimized")
        final_result.quality_score = min(10, report.overall_quality + 2)
        
        self.history.append({
            "stage": "optimize",
            "output": optimized_content,
            "quality_improvement": f"{report.overall_quality} → {final_result.quality_score}"
        })
        
        return final_result
    
    # ========== 完整流程 ==========
    
    def run(self, user_input: str) -> Dict:
        """完整三步法运行"""
        print(f"\n{'='*60}")
        print(f"🎯 用户需求：{user_input}")
        print(f"{'='*60}")
        
        # 第一步：执行
        print(f"\n{'─'*40}")
        print("1️⃣ [执行阶段] 生成初始结果...")
        print(f"{'─'*40}")
        raw = self.execute(user_input)
        print(f"原始输出：\n{raw.content}")
        
        # 第二步：反思
        print(f"\n{'─'*40}")
        print("2️⃣ [反思阶段] 自我检查...")
        print(f"{'─'*40}")
        report = self.reflect(user_input, raw)
        print(f"质量评分：{report.overall_quality}/10")
        print(f"严重程度：{report.severity}")
        print(f"发现问题：")
        for i, issue in enumerate(report.found_issues, 1):
            print(f"  {i}. ❌ {issue}")
        print(f"改进建议：")
        for i, imp in enumerate(report.improvements, 1):
            print(f"  {i}. 💡 {imp}")
        
        # 第三步：优化
        print(f"\n{'─'*40}")
        print("3️⃣ [优化阶段] 迭代改进...")
        print(f"{'─'*40}")
        final = self.optimize(user_input, raw, report)
        print(f"优化后输出：\n{final.content}")
        
        # 汇总
        print(f"\n{'─'*40}")
        print(f"📊 质量提升：{raw.quality_score}/10 → {final.quality_score}/10")
        print(f"✅ 经过 {len(self.history)} 步完成优化")
        print(f"{'─'*40}")
        
        return {
            "user_input": user_input,
            "initial_output": raw.content,
            "issues_found": report.found_issues,
            "improvements": report.improvements,
            "final_output": final.content,
            "quality_improvement": f"{raw.quality_score} → {final.quality_score}"
        }


# ====================================================================
#  第三部分：三层反射架构（工业级）
# ====================================================================

class ResultLayerChecker:
    """第一层：结果层纠错 - 检查输出质量"""
    
    @staticmethod
    def check(output: str, requirements: List[str]) -> Dict:
        """检查输出结果"""
        checks = []
        issues = []
        
        for req in requirements:
            if req in output:
                checks.append({"requirement": req, "passed": True})
            else:
                checks.append({"requirement": req, "passed": False})
                issues.append(f"缺少要求：{req}")
        
        # 检查长度
        if len(output) < 50:
            issues.append("输出内容过短")
        
        # 检查幻觉关键词
        hallucination_keywords = ["可能", "也许", "大概", "不确定"]
        for kw in hallucination_keywords:
            if kw in output:
                issues.append(f"存在不确定性表述：'{kw}'")
        
        return {
            "layer": "result_layer",
            "checks": checks,
            "issues": issues,
            "passed": len(issues) == 0,
            "pass_rate": f"{sum(1 for c in checks if c['passed'])}/{len(checks)}" if checks else "N/A"
        }


class ProcessLayerChecker:
    """第二层：过程层纠错 - 检查执行过程"""
    
    @staticmethod
    def check(expected_steps: List[str], actual_steps: List[str], 
              tool_calls: List[Dict]) -> Dict:
        """检查执行过程"""
        issues = []
        
        # 检查步骤完整性
        missing = [s for s in expected_steps if s not in actual_steps]
        if missing:
            issues.append(f"缺少步骤：{missing}")
        
        extra = [s for s in actual_steps if s not in expected_steps]
        if extra:
            issues.append(f"多余的步骤：{extra}")
        
        # 检查工具调用
        for call in tool_calls:
            if call.get("error"):
                issues.append(f"工具调用出错：{call['tool']} - {call['error']}")
        
        return {
            "layer": "process_layer",
            "issues": issues,
            "passed": len(issues) == 0,
            "completed": len(actual_steps),
            "expected": len(expected_steps)
        }


class ExperienceLayerChecker:
    """第三层：经验层纠错 - 沉淀学习"""
    
    def __init__(self):
        self.experience_store: List[Dict] = []
    
    def check(self, current_result: Dict, past_patterns: List[str]) -> Dict:
        """检查是否有重蹈覆辙"""
        issues = []
        
        for pattern in past_patterns:
            if any(pattern in str(v) for v in current_result.values()):
                issues.append(f"重复错误：'{pattern}' 再次出现")
        
        # 沉淀经验
        experience = {
            "timestamp": "now",
            "patterns": past_patterns,
            "new_patterns": issues,
            "suggestion": "记录本次经验到长期记忆" if not issues else "需要加强此类错误的防护"
        }
        self.experience_store.append(experience)
        
        return {
            "layer": "experience_layer",
            "issues": issues,
            "passed": len(issues) == 0,
            "repeated_errors": issues,
            "total_experiences": len(self.experience_store)
        }


class IndustrialReflexionSystem:
    """
    工业级三层反射系统
    
    三层递进式自查闭环：
    1. 结果层：检查输出质量
    2. 过程层：复盘执行过程
    3. 经验层：沉淀学习经验
    """
    
    def __init__(self):
        self.result_checker = ResultLayerChecker()
        self.process_checker = ProcessLayerChecker()
        self.experience_checker = ExperienceLayerChecker()
        self.all_reports: List[Dict] = []
    
    def full_check(self, 
                   output: str, 
                   requirements: List[str],
                   expected_steps: List[str],
                   actual_steps: List[str],
                   tool_calls: List[Dict],
                   past_patterns: List[str]) -> Dict:
        """三层全量检查"""
        print(f"\n{'='*50}")
        print("🔍 三层反射检查开始")
        print(f"{'='*50}")
        
        # 第一层：结果层
        print(f"\n📋 第一层：结果层纠错")
        result_report = self.result_checker.check(output, requirements)
        print(f"   检查项：{result_report['pass_rate']}")
        for issue in result_report['issues']:
            print(f"   ❌ {issue}")
        
        # 第二层：过程层
        print(f"\n📋 第二层：过程层纠错")
        process_report = self.process_checker.check(expected_steps, actual_steps, tool_calls)
        print(f"   步骤完成：{process_report['completed']}/{process_report['expected']}")
        for issue in process_report['issues']:
            print(f"   ❌ {issue}")
        
        # 第三层：经验层
        print(f"\n📋 第三层：经验层纠错")
        experience_report = self.experience_checker.check(
            {"output": output}, past_patterns
        )
        if experience_report['issues']:
            for issue in experience_report['issues']:
                print(f"   ❌ {issue}")
        else:
            print(f"   ✅ 未发现重复错误，累计经验{experience_report['total_experiences']}条")
        
        full_report = {
            "result_layer": result_report,
            "process_layer": process_report,
            "experience_layer": experience_report,
            "all_passed": result_report['passed'] and process_report['passed'] and experience_report['passed']
        }
        
        self.all_reports.append(full_report)
        return full_report


# ====================================================================
#  第四部分：无反射Agent vs 带反射Agent 对比
# ====================================================================

class SimpleAgent:
    """无反射的普通Agent - 一次输出，不检查"""
    
    def __init__(self):
        self.llm = MockLLM()
    
    def run(self, user_input: str) -> str:
        """一次执行，直接返回，无校验"""
        return self.llm.call(user_input)


def compare_agents():
    """对比无反射Agent和带反射Agent的效果"""
    print(f"\n{'='*60}")
    print("📊 无反射Agent vs 带反射Agent 效果对比")
    print(f"{'='*60}")
    
    test_cases = [
        "帮我写一份本周工作总结周报",
        "分析2024年AI Agent市场",
        "帮我写一个数据处理函数"
    ]
    
    for case in test_cases:
        print(f"\n{'─'*50}")
        print(f"📌 测试任务：{case}")
        print(f"{'─'*50}")
        
        # 无反射Agent
        print(f"\n【无反射Agent】")
        simple = SimpleAgent()
        simple_result = simple.run(case)
        print(f"输出：{simple_result[:100]}...")
        print(f"状态：一次输出，不做检查 ✅/❌ 全靠运气")
        
        # 带反射Agent
        print(f"\n【带反射Agent】")
        reflex = ReflexionAgent()
        reflex_result = reflex.run(case)
        
        print(f"\n{'─'*40}")
        print(f"💡 对比结论")
        print(f"{'─'*40}")
        print(f"  • 无反射Agent：{len(simple_result)}字，无校验，直接交付")
        print(f"  • 带反射Agent：发现{len(reflex_result['issues_found'])}个问题，")
        print(f"    质量从{reflex_result['quality_improvement']}")
        print(f"  • 提升：通过三层反射确保输出质量")
        print(f"{'─'*40}")


# ====================================================================
#  第五部分：核心技巧演示
# ====================================================================

def demonstrate_tips():
    """演示3个核心开发技巧"""
    print(f"\n{'='*60}")
    print("💡 核心开发技巧演示")
    print(f"{'='*60}")
    
    # 技巧1：分离执行和审核角色
    print(f"\n{'─'*40}")
    print("技巧1：分离[执行角色]和[审核角色]")
    print(f"{'─'*40}")
    print("""
✅ 正确做法：
  角色A（执行者）：完成用户任务
  角色B（审核者）：检查A的输出
  → 不同角色、不同Prompt、独立逻辑

❌ 错误做法：
  同一个AI既执行又审核
  → 自己查自己，容易忽略问题
""")
    
    # 技巧2：固定自查维度
    print(f"\n{'─'*40}")
    print("技巧2：固定自查维度，不要模糊检查")
    print(f"{'─'*40}")
    print("""
✅ 正确做法（6个明确维度）：
  1. 事实幻觉检查
  2. 需求覆盖检查
  3. 逻辑一致性检查
  4. 格式规范性检查
  5. 安全合规检查
  6. 完整性检查

❌ 错误做法：
  "帮我检查一下有没有问题"
  → AI不知道查什么，效果差
""")
    
    # 技巧3：轻量vs复杂分层
    print(f"\n{'─'*40}")
    print("技巧3：轻量任务单层自查，复杂任务三层自查")
    print(f"{'─'*40}")
    print("""
📌 简单文案、问答 → 结果层自查（高效不冗余）
  - 只需检查内容质量和格式

📌 复杂报告、分析 → 三层全量自查（稳准可靠）
  - 结果层：检查输出质量
  - 过程层：复盘执行过程
  - 经验层：沉淀学习经验
""")


# ====================================================================
#  第六部分：主程序
# ====================================================================

def main():
    """主函数：运行所有演示"""
    print("=" * 60)
    print("🔄 Agent反射与自我纠错 — Reflexion反射机制完整实现")
    print("=" * 60)
    print("\n覆盖内容：")
    print("  ✅ 普通Agent缺陷分析")
    print("  ✅ Reflexion三步法（执行→反思→优化）")
    print("  ✅ 三层反射架构（结果层/过程层/经验层）")
    print("  ✅ 反射与四大组件的联动")
    print("  ✅ 无反射 vs 带反射效果对比")
    print("  ✅ 3个核心开发技巧")
    
    while True:
        print(f"\n{'='*50}")
        print("请选择演示模式：")
        print("  1. Reflexion三步法完整演示（核心）")
        print("  2. 三层反射架构演示（工业级）")
        print("  3. 无反射 vs 带反射 效果对比")
        print("  4. 核心开发技巧演示")
        print("  5. 全部演示")
        print("  0. 退出")
        print(f"{'='*50}")
        
        choice = input("\n请输入选项（0-5）：").strip()
        
        if choice == "1":
            agent = ReflexionAgent()
            agent.run("帮我写一份本周工作总结周报")
        
        elif choice == "2":
            system = IndustrialReflexionSystem()
            report = system.full_check(
                output="本周工作完成。项目A进展顺利。",
                requirements=["本周", "工作", "项目", "进展"],
                expected_steps=["收集数据", "分析", "生成报告", "检查"],
                actual_steps=["收集数据", "生成报告"],
                tool_calls=[{"tool": "search", "error": None}],
                past_patterns=["缺少数据", "格式不规范"]
            )
            print(f"\n📊 三层检查汇总：")
            print(f"  结果层：{'✅ 通过' if report['result_layer']['passed'] else '❌ 未通过'}")
            print(f"  过程层：{'✅ 通过' if report['process_layer']['passed'] else '❌ 未通过'}")
            print(f"  经验层：{'✅ 通过' if report['experience_layer']['passed'] else '❌ 未通过'}")
            print(f"  全部通过：{'✅ 是' if report['all_passed'] else '❌ 否'}")
        
        elif choice == "3":
            compare_agents()
        
        elif choice == "4":
            demonstrate_tips()
        
        elif choice == "5":
            print("\n🔥 运行全部演示...")
            agent = ReflexionAgent()
            agent.run("帮我写一份本周工作总结周报")
            
            system = IndustrialReflexionSystem()
            system.full_check(
                output="本周工作完成。项目A进展顺利。",
                requirements=["本周", "工作", "项目", "进展"],
                expected_steps=["收集数据", "分析", "生成报告", "检查"],
                actual_steps=["收集数据", "生成报告"],
                tool_calls=[{"tool": "search", "error": None}],
                past_patterns=["缺少数据", "格式不规范"]
            )
            
            compare_agents()
            demonstrate_tips()
        
        elif choice == "0":
            print("感谢使用，再见！")
            break
        
        else:
            print("无效选项，请重新选择")


if __name__ == "__main__":
    main()
