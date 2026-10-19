#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第11篇配套完整项目代码 · crew_mock.py
CrewAI 兼容的轻量模拟引擎（无需安装crewai即可跑通多Agent协作）

实现与 CrewAI 一致的四个核心概念（对应文章第二章）：
  Agent   —— 团队成员（角色/目标/背景）
  Task    —— 工作任务（描述/期望输出/负责人）
  Crew    —— 项目组（组织Agent和Task）
  Process —— 流程（顺序执行 → 结果传递）
==========================================================================
"""

from typing import Any, Dict, List, Optional


class Agent:
    """CrewAI 兼容的 Agent 定义"""
    
    def __init__(self, role: str, goal: str, backstory: str = "",
                 llm=None, verbose: bool = True):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.llm = llm
        self.verbose = verbose
    
    def __repr__(self):
        return f"Agent(role={self.role})"


class Task:
    """CrewAI 兼容的 Task 定义
    
    关键：必须声明 expected_output，否则Agent难以稳定交付（文章调试建议2）
    """
    
    def __init__(self, description: str, expected_output: str,
                 agent: Agent):
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
    
    def __repr__(self):
        return f"Task(agent={self.agent.role}, output={self.expected_output[:20]}...)"


class Process:
    """执行流程类型"""
    SEQUENTIAL = "sequential"     # 顺序执行（入门首选）
    HIERARCHICAL = "hierarchical"  # 层级执行（进阶）


# ======================================================================
# 模拟LLM：为不同角色产出符合职责的内容
# ======================================================================

class MockRoleLLM:
    """按角色生成内容的模拟LLM"""
    
    @staticmethod
    def _extract_topic(text: str) -> str:
        """从文本中提取主题：优先引号，其次一级标题，再次"主题："标记"""
        import re
        m = re.search(r"[“\"]([^”\"]{2,40})[”\"]", text)
        if m:
            return m.group(1)
        m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        if m:
            return m.group(1).strip()
        m = re.search(r"主题[：:]\s*(\S[^\n，。]{1,40})", text)
        if m:
            return m.group(1).strip().rstrip("】]）) ")
        return ""
    
    def think(self, role: str, description: str, context: str = "") -> str:
        topic = self._extract_topic(description) or self._extract_topic(context) or "AI Agent"
        
        if "研究员" in role:
            return f"""【结构化资料清单 · 主题：{topic}】
一、背景
{topic} 是当前AI应用落地的重点方向。随着大模型能力提升，相关场景逐步成熟。

二、核心观点
1. 降本：自动化处理高频重复任务，减少人力投入。
2. 提效：响应速度从小时级缩短到秒级。
3. 7×24服务：覆盖非工作时间。
4. 复杂问题转接：超出能力边界时平滑转人工。

三、关键数据
- 响应时长：平均<3秒
- 重复咨询拦截率：约80%
- 用户满意度：提升15-20个百分点

四、应用案例
1. 售前咨询：产品介绍、价格解答
2. 售后故障排查：引导自助解决
3. 订单查询：自动查询并回复
4. 智能分诊：按问题类型分配"""
        
        if "撰稿人" in role:
            return f"""# {topic}

## 一、引言
{topic}正在从概念走向落地。本文基于研究资料，梳理其价值、现状与实践路径。

## 二、正文
### 2.1 为什么需要它
传统模式依赖人力，成本高、响应慢、难以7×24覆盖。{topic}通过智能体技术缓解这些问题。

### 2.2 核心能力
- 自动化处理：拦截约80%的重复咨询
- 快速响应：平均响应低于3秒
- 持续在线：7×24小时服务
- 平滑转接：复杂问题移交人工

### 2.3 落地案例
覆盖售前咨询、售后排查、订单查询、智能分诊四类场景，满意度提升15-20个百分点。

## 三、结论
{topic}的价值已被验证，建议先从小场景验证，再逐步扩展。"""
        
        if "审核" in role:
            return f"""【最终报告（审核优化版）】

# {topic}

## 引言
{topic}已进入实际落地阶段，核心价值在于降本、提效与全天候服务。

## 正文
### 核心能力
1. 自动化拦截约80%的重复咨询
2. 平均响应时长低于3秒
3. 7×24小时持续在线
4. 复杂问题平滑转人工

### 典型场景
售前咨询、售后排查、订单查询、智能分诊。

## 结论
建议先小场景验证，再逐步扩展，用户满意度可提升15-20个百分点。

---
【修改说明】
1. 补强了数据支撑（拦截率、响应时长、满意度）
2. 精简了重复表述，结构更紧凑
3. 结论增加了"小场景验证"的可执行建议"""
        
        return f"[{role}] 已完成：{description[:40]}"


# ======================================================================
# Crew：项目组（核心调度）
# ======================================================================

class Crew:
    """CrewAI 兼容的 Crew
    
    - 顺序执行：上一个Task的输出会作为下一个Task的上下文（结果传递）
    - verbose=True 打印每个Agent的执行过程
    """
    
    def __init__(self, agents: List[Agent], tasks: List[Task],
                 process: str = Process.SEQUENTIAL, verbose: bool = True):
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.verbose = verbose
        self.mock_llm = MockRoleLLM()
        self.outputs: List[Dict[str, str]] = []
    
    def _format_task(self, task: Task, inputs: Dict[str, Any]) -> str:
        """替换 task.description 中的 {变量}"""
        desc = task.description
        for k, v in inputs.items():
            desc = desc.replace("{" + k + "}", str(v))
        return desc
    
    def kickoff(self, inputs: Optional[Dict[str, Any]] = None) -> str:
        """启动团队执行（顺序流程 + 结果传递）"""
        inputs = inputs or {}
        
        if self.verbose:
            print("\n" + "=" * 62)
            print(f"👥 Crew 启动 | 成员{len(self.agents)}人 | 任务{len(self.tasks)}个 | 流程：{self.process}")
            print("=" * 62)
        
        context = ""
        for i, task in enumerate(self.tasks, 1):
            desc = self._format_task(task, inputs)
            
            if self.verbose:
                print(f"\n{'─'*62}")
                print(f"📌 任务{i}/{len(self.tasks)} | 负责人：{task.agent.role}")
                print(f"   任务描述：{desc[:80]}...")
                print(f"   期望输出：{task.expected_output}")
                print(f"{'─'*62}")
            
            # Agent执行（带上下文 → 结果传递）
            result = self.mock_llm.think(task.agent.role, desc, context)
            
            if self.verbose:
                print(f"   ✅ {task.agent.role} 输出（{len(result)}字）：")
                preview = result.strip().split("\n")[:3]
                for line in preview:
                    print(f"      {line}")
            
            self.outputs.append({
                "task": task.expected_output,
                "agent": task.agent.role,
                "output": result,
            })
            context = result  # 结果传递给下一个任务
        
        final = self.outputs[-1]["output"] if self.outputs else ""
        
        if self.verbose:
            print("\n" + "=" * 62)
            print("🎉 Crew 协作完成！")
            print("=" * 62)
        
        return final
    
    def _extract_topic(self, text: str) -> str:
        import re
        m = re.search(r"[“\"]([^”\"]{2,40})[”\"]", text)
        return m.group(1) if m else ""
