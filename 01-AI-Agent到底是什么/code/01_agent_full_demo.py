#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
 第1篇配套完整演示代码
 AI Agent 到底是什么？—— 告别玄学，一文读懂智能体的本质
==========================================================================

 本文件为《AI Agent 零基础实战》第1篇的配套完整项目代码。
 使用纯 Python 模拟后端（Mock API），无需任何外部依赖即可直接运行。
 覆盖文中全部技术点：

   ✅ 普通大模型 vs AI Agent 的直观对比演示
   ✅ Agent 四个核心特质（自主目标、任务拆解、工具联动、记忆迭代）
   ✅ 6 个应用场景模拟
   ✅ 核心差异表 6 维度对比

 运行方式：
   python 01_agent_full_demo.py

 作者：AI Agent 零基础实战
 版本：1.0
==========================================================================
"""

import json
import time
import random
import textwrap
from typing import Any, Optional
from dataclasses import dataclass, field


# =========================================================================
#  第一部分：模拟后端基础设施（Mock API）
#  无需真实 API Key，完全模拟大模型的行为
# =========================================================================

class MockLLM:
    """模拟大模型 API 调用 —— 模拟后端，无需真实 Key"""

    def __init__(self, model_name: str = "mock-gpt-4"):
        self.model_name = model_name
        self.call_count = 0

    def chat(self, prompt: str, system: Optional[str] = None,
             temperature: float = 0.7) -> str:
        """模拟大模型的 chat 响应"""
        self.call_count += 1

        # 模拟延迟
        time.sleep(0.05)

        if not system:
            system = "你是一个通用AI助手。"

        # ---------------------------------------------------------------
        # 以下为模拟的"模型回复"，用关键词匹配模拟不同场景
        # ● 普通问答模式：只返回简单的回答，不主动拆解/规划
        # ● Agent 模式：返回结构化的规划、工具调用、反思结果
        # ---------------------------------------------------------------

        # 1) 模拟普通大模型（被动回答）—— 返回简单回复
        if "【普通模式】" in prompt:
            return self._simple_reply(prompt)

        # 2) 模拟 Agent 拆解规划
        if "拆解任务" in prompt or "【规划】" in prompt:
            return self._plan_reply(prompt)

        # 3) 模拟 Agent 工具调用
        if "【工具】" in prompt:
            return self._tool_reply(prompt)

        # 4) 模拟 Agent 自我反思/迭代
        if "【反思】" in prompt or "【迭代】" in prompt:
            return self._reflect_reply(prompt)

        # 5) 模拟 6 个场景的特定回复
        if "【职场日报】" in prompt:
            return self._workplace_report()

        if "【知识库问答】" in prompt:
            return self._knowledge_base_reply(prompt)

        if "【数据分析】" in prompt:
            return self._data_analysis_reply(prompt)

        if "【全网调研】" in prompt:
            return self._research_reply(prompt)

        if "【内容创作】" in prompt:
            return self._content_creation_reply(prompt)

        if "【私人助手】" in prompt:
            return self._personal_assistant_reply(prompt)

        # 默认：通用有礼貌的回复
        return f"[{self.model_name} 回复]：已收到您的问题。{(prompt[:60] + '...') if len(prompt) > 60 else prompt}"

    # ---- 内部模拟回复 ----

    def _simple_reply(self, prompt: str) -> str:
        """模拟普通大模型：只基于字面内容一次性回复"""
        return (
            "基于您提供的文字，我做了以下总结：\n"
            "1. 这是您给的内容。\n"
            "2. 信息可能不完整。\n"
            "3. 如果有更多资料请补充。\n"
            "\n[提示：本回复来自于普通问答模式，不会主动规划、不会主动搜索、"
            "不会校验结果完整性。信息缺失时只能被动等待用户补充。]"
        )

    def _plan_reply(self, prompt: str) -> str:
        return json.dumps({
            "thought": "我已理解任务目标，正在拆解为可执行的子任务并确定执行顺序。",
            "plan": [
                {"step": 1, "action": "信息收集", "detail": "检索相关数据和资料"},
                {"step": 2, "action": "内容整理", "detail": "对信息进行分类和筛选"},
                {"step": 3, "action": "分析提炼", "detail": "提取关键要点和结论"},
                {"step": 4, "action": "格式输出", "detail": "按照要求格式生成最终结果"},
                {"step": 5, "action": "自我校验", "detail": "检查输出完整性和准确度"}
            ]
        }, ensure_ascii=False, indent=2)

    def _tool_reply(self, prompt: str) -> str:
        if "搜索" in prompt or "search" in prompt.lower():
            return (
                "【工具调用：联网搜索】\n"
                "✓ 已调用搜索引擎 API\n"
                "✓ 获取到 3 条相关结果\n"
                "✓ 已提取关键信息\n"
                "结果摘要：已为您检索到最新相关信息。"
            )
        if "计算" in prompt or "calc" in prompt.lower():
            return (
                "【工具调用：计算器】\n"
                "✓ 已调用计算模块\n"
                "✓ 执行运算完成\n"
                f"计算结果：{sum(random.randint(1, 100) for _ in range(5))}"
            )
        if "文件" in prompt or "file" in prompt.lower():
            return (
                "【工具调用：文件操作】\n"
                "✓ 已读取目标文件\n"
                "✓ 文件内容解析成功\n"
                "✓ 关键数据已提取"
            )
        return (
            "【工具调用结果】\n"
            "✓ 工具执行成功\n"
            "✓ 结果已整合到当前上下文"
        )

    def _reflect_reply(self, prompt: str) -> str:
        if "自我反思" in prompt or "纠错" in prompt:
            return json.dumps({
                "reflection": "正在检查本次执行结果...",
                "issues_found": [
                    "发现第2部分数据不完整",
                    "发现格式需要调整"
                ],
                "fix_plan": "准备重新补充数据和优化格式",
                "status": "重新执行中"
            }, ensure_ascii=False, indent=2)
        return json.dumps({
            "iteration_round": 2,
            "improvements": [
                "补充了缺失数据",
                "优化了结构排版",
                "增加了数据校验"
            ],
            "status": "优化完成，质量提升"
        }, ensure_ascii=False, indent=2)

    def _workplace_report(self) -> str:
        return json.dumps({
            "daily_report": {
                "date": time.strftime("%Y-%m-%d"),
                "summary": "今日完成核心项目开发、会议沟通、文档整理三项重点工作。",
                "key_works": [
                    {"item": "智能体框架重构", "status": "完成", "note": "核心模块已通过测试"},
                    {"item": "项目周会", "status": "完成", "note": "确认了下阶段三个关键节点"},
                    {"item": "技术方案文档", "status": "进行中", "note": "预计明天定稿"}
                ],
                "unfinished": [
                    "技术方案评审（待安排会议）",
                    "性能测试报告（数据收集中）"
                ],
                "tomorrow_plan": [
                    "完成技术方案评审",
                    "开始性能测试数据采集",
                    "准备周报数据汇总"
                ]
            }
        }, ensure_ascii=False, indent=2)

    def _knowledge_base_reply(self, prompt: str) -> str:
        return (
            "【知识库检索结果】\n"
            "✓ 命中 2 篇相关文档\n"
            "✓ 匹配度：92.5%\n"
            f"\n回答：根据知识库中《{random.choice(['产品手册V3.2', '技术规范2025', '操作指南', 'FAQ合集'])}》"
            f"第{random.randint(2, 8)}节相关内容，"
            "您询问的问题可以分为以下要点：\n"
            "1. 核心概念阐述\n"
            "2. 操作步骤说明\n"
            "3. 注意事项与常见问题\n"
            "\n[以上回答基于本地知识库，不依赖大模型预训练知识]"
        )

    def _data_analysis_reply(self, prompt: str) -> str:
        return json.dumps({
            "data_analysis_result": {
                "data_source": "Excel_2025Q1_sales.xlsx",
                "data_quality": {
                    "total_rows": 1047,
                    "missing_values": "2.3%（已自动清洗）",
                    "outliers": "发现3个异常值已标记"
                },
                "key_insights": [
                    "Q1总营收环比增长18.6%，超出目标3.2个百分点",
                    "B产品线增速最快（+34.2%），成为新增长极",
                    "华东区连续3个月排名第一，贡献35%的营收"
                ],
                "visualization": "已生成趋势图、占比图、对比图（模拟）",
                "recommendation": "建议加大B产品线投入，重点关注华北区增长潜力"
            }
        }, ensure_ascii=False, indent=2)

    def _research_reply(self, prompt: str) -> str:
        return json.dumps({
            "research_report": {
                "topic": "AI Agent 行业最新动态",
                "source_count": 12,
                "search_keywords": ["AI Agent 2025趋势", "智能体应用落地"],
                "main_findings": [
                    "全球AI Agent市场规模预计2027年达420亿美元，年复合增长率45%",
                    "企业级Agent落地集中在客服、数据分析和流程自动化三大领域",
                    "开源Agent框架生态快速成熟，LangChain、AutoGPT等社区活跃",
                    "多智能体协作成为2025年最热门方向之一"
                ],
                "conclusion": "AI Agent正从概念验证迈向规模化落地，是当前最具价值的AI应用方向。",
                "disclaimer": "报告基于联网检索整理，来源已筛选去重，保持时效性。"
            }
        }, ensure_ascii=False, indent=2)

    def _content_creation_reply(self, prompt: str) -> str:
        return json.dumps({
            "content_creation": {
                "pipeline": "选题策划 → 大纲生成 → 初稿撰写 → AI润色 → 排版输出",
                "article": {
                    "title": "AI Agent到底是什么？一文讲透智能体的本质",
                    "outline": [
                        "引言：为什么需要理解AI Agent",
                        "一、普通AI vs AI Agent的核心差异",
                        "二、AI Agent的四大核心特质",
                        "三、普通人可落地的Agent场景",
                        "四、总结与展望"
                    ],
                    "estimated_read_time": "约5分钟",
                    "tone": "通俗易懂 + 技术干货"
                },
                "collaboration": "本内容由【选题Agent+写作Agent+润色Agent】多智能体协作完成"
            }
        }, ensure_ascii=False, indent=2)

    def _personal_assistant_reply(self, prompt: str) -> str:
        return (
            "【私人助手回复】\n"
            f"✓ 读取了您的历史记录（共{random.randint(30, 200)}条交互）\n"
            "✓ 了解您的学习进度、兴趣偏好、时间安排\n"
            "\n建议如下：\n"
            "1. 基于您过去两周的学习记录，本周重点建议继续深入Agent开发实战\n"
            "2. 您习惯每晚8-10点学习，已为您预留今日学习时段\n"
            "3. 根据您的理解程度，推荐开始阅读『任务规划模块』实战章节\n"
            "4. 提醒：您上周设定的『完成第1篇代码实战』目标还未标记完成\n"
            "\n[以上内容基于您的个人画像和记忆数据量身定制]"
        )


# =========================================================================
#  第二部分：普通大模型（模拟）
#  特点：被动响应、单次问答、无工具、无记忆、无纠错
# =========================================================================

class SimpleChatModel:
    """模拟『普通大模型』—— 只会被动回答的问答工具"""

    def __init__(self, name: str = "普通AI助手"):
        self.name = name
        self.llm = MockLLM()
        self.chat_history: list[dict] = []

    def ask(self, user_input: str) -> str:
        """普通大模型：用户不提问就不动作，一次一问"""
        prompt = f"【普通模式】用户问：{user_input}"

        # 简单拼接历史（仅保留最近 2 轮，且只是拼接不真正理解）
        context = ""
        if self.chat_history:
            recent = self.chat_history[-2:]
            context = "历史记录：" + " | ".join(
                f"Q:{h['q']} A:{h['a'][:30]}..." for h in recent
            ) + "\n"

        full_prompt = context + prompt if context else prompt
        reply = self.llm.chat(full_prompt)
        self.chat_history.append({"q": user_input, "a": reply})
        return reply

    def __str__(self) -> str:
        return f"【{self.name}】被动问答 | 无工具 | 无规划 | 无纠错"


# =========================================================================
#  第三部分：AI Agent 核心引擎
#  包含四大核心特质：自主目标 / 拆解规划 / 工具联动 / 记忆迭代
# =========================================================================

# ---- 工具集 ----

class ToolRegistry:
    """Agent 可调用的工具集合 —— 模拟后端"""

    @staticmethod
    def web_search(query: str) -> str:
        """模拟联网搜索"""
        results = {
            "AI Agent 2025": "全球AI Agent市场2027年预计达420亿美元...",
            "智能体开发框架": "LangChain、AutoGPT、MetaGPT等框架快速发展...",
            "Python教程": "Python官方最新版本为3.13，新增特性包括...",
        }
        for k, v in results.items():
            if k.lower() in query.lower():
                return f"[搜索] {k}: {v}"
        return f"[搜索] 找到关于「{query}」的相关结果 3 条（模拟数据）"

    @staticmethod
    def calculator(expression: str) -> str:
        """模拟计算器"""
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"[计算] {expression} = {result}"
        except Exception:
            return f"[计算] 表达式「{expression}」无法计算"

    @staticmethod
    def read_file(filename: str) -> str:
        """模拟读取文件"""
        mock_files = {
            "sales_data.xlsx": "日期,产品,销量,金额\n2025-01,Q1,1200,36000\n2025-02,新品,980,49000",
            "meeting_notes.txt": "会议主题：Q2产品规划\n参会人：张伟、李娜、王磊\n决议：下月启动B版本开发",
            "report_template.docx": "周报模板：本周工作/下周计划/待办事项/风险项",
        }
        return mock_files.get(filename,
                              f"[文件] 已读取 {filename}，内容解析完成（模拟）")

    @staticmethod
    def write_file(filename: str, content: str) -> str:
        """模拟写入文件"""
        return f"[文件] 已写入 {filename}，大小约 {len(content)} 字符（模拟）"

    @staticmethod
    def excel_analyze(filename: str) -> str:
        """模拟 Excel 数据分析"""
        return (
            f"[数据分析] {filename}：\n"
            "  - 总计 8 行 4 列\n"
            "  - 缺失值：0\n"
            "  - 数值列均值：32,450\n"
            "  - 初步结论：Q1 环比增长 +18.6%"
        )

    @staticmethod
    def query_database(sql: str) -> str:
        """模拟数据库查询"""
        return (
            f"[数据库] 执行 SQL：{sql[:50]}...\n"
            "  - 返回 3 行结果\n"
            "  - 查询耗时 23ms"
        )


# ---- 记忆系统 ----

@dataclass
class MemoryItem:
    """单条记忆"""
    role: str        # user / agent / tool
    content: str
    timestamp: float = field(default_factory=time.time)


class MemorySystem:
    """三级记忆架构：

    Level 1 - 短期记忆（对话上下文，当前会话）
    Level 2 - 长期记忆（关键信息，持久化存储）
    Level 3 - 工作记忆（当前任务中的中间状态）
    """

    def __init__(self, max_short_term: int = 20):
        self.short_term: list[MemoryItem] = []
        self.long_term: dict[str, Any] = {
            "user_name": None,
            "user_preferences": {},
            "learned_patterns": [],
            "past_errors": [],
            "key_decisions": [],
        }
        self.working_memory: dict[str, Any] = {
            "current_goal": None,
            "current_plan": [],
            "step_index": 0,
            "tool_results": [],
            "intermediate_outputs": [],
        }
        self.max_short_term = max_short_term

    def add(self, role: str, content: str):
        """写入短期记忆"""
        self.short_term.append(MemoryItem(role=role, content=content))
        # 记忆上限裁剪
        if len(self.short_term) > self.max_short_term:
            self.short_term = self.short_term[-self.max_short_term:]

    def remember(self, key: str, value: Any):
        """写入长期记忆"""
        self.long_term[key] = value

    def recall(self, key: str) -> Any:
        """读取长期记忆"""
        return self.long_term.get(key)

    def get_context(self, window: int = 6) -> str:
        """从短期记忆构建上下文摘要"""
        recent = self.short_term[-window:] if len(self.short_term) > window else self.short_term
        lines = []
        for item in recent:
            label = "🧑" if item.role == "user" else "🤖"
            content = item.content[:80] + ("..." if len(item.content) > 80 else "")
            lines.append(f"{label} {content}")
        return "\n".join(lines)

    def mark_error(self, error: str):
        """记录错误供迭代优化"""
        self.long_term["past_errors"].append({
            "error": error,
            "time": time.time()
        })

    def summarize(self) -> str:
        """输出记忆摘要"""
        return (
            f"短期记忆：{len(self.short_term)} 条\n"
            f"长期记忆：{sum(1 for v in self.long_term.values() if v)} 项\n"
            f"已记录错误：{len(self.long_term['past_errors'])} 次\n"
            f"当前任务进度：第 {self.working_memory['step_index']}/{len(self.working_memory['current_plan'])} 步"
        )


# ---- 规划器 ----

class Planner:
    """任务规划器 —— 将复杂目标拆解为可执行步骤"""

    def __init__(self, llm: MockLLM):
        self.llm = llm

    def decompose(self, goal: str) -> list[dict]:
        """将目标拆解为步骤序列"""
        plan_prompt = f"【规划】拆解任务：{goal}"
        plan_str = self.llm.chat(plan_prompt)

        try:
            plan_data = json.loads(plan_str)
            return plan_data.get("plan", [])
        except (json.JSONDecodeError, AttributeError):
            # 降级：通用拆解
            return [
                {"step": 1, "action": "理解需求", "detail": f"分析任务目标：{goal[:30]}..."},
                {"step": 2, "action": "收集信息", "detail": "调用工具获取必要数据"},
                {"step": 3, "action": "加工处理", "detail": "对信息进行分析整理"},
                {"step": 4, "action": "生成输出", "detail": "按格式生成最终结果"},
                {"step": 5, "action": "质量校验", "detail": "自我检查并修正"},
            ]


# ---- 核心 Agent ----

class AIAgentCore:
    """
    AI Agent 核心引擎 —— 具备四个核心特质：

    ✦ 自主目标意识 —— 给定目标就能自主推进
    ✦ 任务拆解规划 —— 复杂任务自动拆分
    ✦ 工具联动执行 —— 自主调用各类工具
    ✦ 记忆迭代优化 —— 记录、反思、持续改进
    """

    def __init__(self, name: str = "AI Agent"):
        self.name = name
        self.llm = MockLLM()
        self.memory = MemorySystem()
        self.planner = Planner(self.llm)
        self.tools = ToolRegistry()
        self.reflection_enabled = True

    def _think(self, prompt: str) -> str:
        """内部思考 —— 调用模拟大模型"""
        return self.llm.chat(prompt)

    # ---------- 特质1：自主目标意识 ----------

    def set_goal(self, goal: str):
        """设定自主目标（不需要逐指令指挥）"""
        self.memory.working_memory["current_goal"] = goal
        self.memory.add("agent",
                        f"[自主目标设定] 已接收并理解目标: {goal}")
        print(f"\n🎯 【自主目标意识】Agent 已接收目标：\n    「{goal}」")
        print(f"    → Agent 开始自主推进任务流程，无需逐指令指挥...")

    # ---------- 特质2：任务拆解规划 ----------

    def plan(self) -> list[dict]:
        """拆解当前目标为可执行步骤"""
        goal = self.memory.working_memory.get("current_goal", "")
        print(f"\n📋 【任务拆解规划】正在将复杂目标拆解为子任务...")

        steps = self.planner.decompose(goal)

        self.memory.working_memory["current_plan"] = steps
        self.memory.working_memory["step_index"] = 0
        self.memory.add("agent",
                        f"[规划] 已拆解为 {len(steps)} 个子任务")

        print(f"    → 拆解完成，共 {len(steps)} 个步骤：")
        for s in steps:
            print(f"      第{s.get('step', '?')}步：{s.get('action', '未知')} "
                  f"— {s.get('detail', '')}")
        return steps

    # ---------- 特质3：工具联动执行 ----------

    def execute_step(self, step: dict) -> str:
        """执行一个步骤，可自动调用工具"""
        action = step.get("action", "")
        detail = step.get("detail", "")
        step_num = step.get("step", "?")
        print(f"\n🔧 【执行第 {step_num} 步】{action}：{detail[:40]}...")

        # 根据步骤动作自动匹配工具
        if "搜索" in action or "收集" in action or "检索" in action:
            result = self.tools.web_search(detail)
        elif "计算" in action or "分析" in action:
            result = self.tools.calculator("1250 + 3800 * 2")
        elif "文件" in action or "读取" in action:
            result = self.tools.read_file("sales_data.xlsx")
        elif "输出" in action or "生成" in action:
            result = self.tools.write_file("output_result.md",
                                           f"步骤{step_num}执行完成")
        else:
            # 默认用模拟大模型处理
            tool_prompt = f"【工具】处理任务 - {action}: {detail}"
            result = self._think(tool_prompt)

        self.memory.working_memory["tool_results"].append({
            "step": step_num,
            "result": result
        })
        self.memory.add("tool", result)
        print(f"    ✓ 执行结果：{result[:80]}...")
        return result

    def execute_plan(self):
        """顺序执行全部规划步骤"""
        plan = self.memory.working_memory.get("current_plan", [])
        print(f"\n⚙️  【工具联动执行】开始按规划顺序执行 {len(plan)} 个步骤...")

        for i, step in enumerate(plan):
            self.memory.working_memory["step_index"] = i + 1
            result = self.execute_step(step)
            self.memory.working_memory["intermediate_outputs"].append(result)

        print(f"\n✅ 全部步骤执行完成！")
        return self.memory.working_memory["intermediate_outputs"]

    # ---------- 特质4：记忆与迭代优化 ----------

    def self_reflection(self) -> dict:
        """自我反思 —— 检查结果并发现问题"""
        if not self.reflection_enabled:
            return {"reflection": "未启用反思"}

        print(f"\n🔄 【记忆与迭代优化】正在进行自我反思...")
        # 组装反思上下文
        context = self.memory.get_context()
        reflect_prompt = (
            f"【反思】【迭代】请基于执行过程进行自我检查：\n{context}"
        )
        result = self._think(reflect_prompt)

        try:
            reflection = json.loads(result)
        except json.JSONDecodeError:
            reflection = {"reflection": result, "issues_found": [], "status": "unknown"}

        issues = reflection.get("issues_found", [])
        if issues:
            print(f"    🔍 发现问题 {len(issues)} 项：")
            for iss in issues:
                print(f"       ⚠ {iss}")
                self.memory.mark_error(str(iss))
        else:
            print(f"    ✅ 未发现明显问题，质量良好")

        return reflection

    def iterate(self, reflection: dict) -> str:
        """根据反思结果进行迭代优化"""
        issues = reflection.get("issues_found", [])
        if not issues:
            return "无需迭代，结果已达标"

        print(f"    🔁 正在执行迭代优化...")
        iteration_prompt = f"【迭代】根据问题修正和优化：{json.dumps(issues, ensure_ascii=False)}"
        result = self._think(iteration_prompt)

        self.memory.add("agent",
                        f"[迭代] 完成了第 {self.llm.call_count} 轮优化")
        print(f"    ✓ 优化完成，质量进一步提升")
        return result

    def summarize_memory(self) -> str:
        """输出当前记忆状态"""
        return self.memory.summarize()

    def run_complete(self, goal: str) -> str:
        """
        一键运行完整 Agent 流程 —— 演示四个核心特质的完整协同

        1. 设定目标（自主目标意识）
        2. 拆解规划（任务拆解规划）
        3. 执行步骤（工具联动执行）
        4. 反思迭代（记忆迭代优化）
        5. 输出最终结果
        """
        print("\n" + "=" * 70)
        print(f"🚀 【{self.name}】开始全流程执行")
        print("=" * 70)

        # 第一步：自主目标
        self.set_goal(goal)

        # 第二步：拆解规划
        steps = self.plan()

        # 第三步：工具联动执行
        outputs = self.execute_plan()

        # 第四步：自我反思 + 迭代优化
        reflection = self.self_reflection()
        self.iterate(reflection)

        print("\n" + "=" * 70)
        print(f"🏁 【{self.name}】目标执行完成！")
        print(f"📊 记忆摘要：{self.summarize_memory()}")
        print(f"📞 调用大模型次数：{self.llm.call_count} 次")
        print("=" * 70)

        final = (
            f"\n【最终交付结果】\n"
            f"目标：{goal}\n"
            f"执行步骤数：{len(steps)}\n"
            f"工具调用次数：{len(self.memory.working_memory['tool_results'])}\n"
            f"反思纠正：{len(self.memory.recall('past_errors'))} 处\n"
        )
        return final

    def __str__(self) -> str:
        return (
            f"【{self.name}】自主目标 | 拆解规划 | 工具联动 "
            f"| 记忆迭代 | 自我纠错"
        )


# =========================================================================
#  第四部分：对比演示 —— 普通大模型 vs AI Agent
#  核心演示：为什么普通AI只能"被动回答"，AI Agent可以"主动干活"
# =========================================================================

def demo_comparison():
    """对比演示：同一个任务，普通大模型 vs AI Agent 的差异"""

    task = (
        "帮我整理本周工作内容，生成一份标准周报，\n"
        "    筛选重点工作，标注未完成任务，并给出下周工作计划"
    )

    print("\n" + "█" * 70)
    print("█  对比演示：普通大模型 vs AI Agent")
    print("█  同一个任务，两种完全不同的表现")
    print("█" * 70)

    # ---- 普通大模型 ----
    print("\n" + "─" * 70)
    print("📌 【普通大模型】表现：")
    print("─" * 70)

    chat = SimpleChatModel()
    print(f"   用户的任务：{task}")
    print(f"\n   模型状态：{chat}")
    print(f"\n   AI 回答：")
    reply = chat.ask(task)
    for line in reply.split("\n"):
        print(f"     {line}")

    print(f"\n   ⚠ 问题分析：")
    print(f"     1. 只基于用户给的文字一次性总结，没有主动追问")
    print(f"     2. 没有拆解步骤（整理→筛选→标注→计划）")
    print(f"     3. 没有调用任何工具补充信息")
    print(f"     4. 没有检查输出完整性")
    print(f"     5. 用户不说「继续」就停止工作")

    # ---- AI Agent ----
    print("\n" + "─" * 70)
    print("📌 【AI Agent】表现：")
    print("─" * 70)

    agent = AIAgentCore("周报助手Agent")
    print(f"   用户的任务：{task}")
    print(f"\n   Agent 状态：{agent}")

    result = agent.run_complete(task + "【职场日报】")

    print(f"\n   ✅ Agent 优势总结：")
    print(f"     1. 自主推进：给定目标后全程自动化执行")
    print(f"     2. 分步处理：拆成 5 个有序步骤逐一完成")
    print(f"     3. 工具调用：自动调用搜索、计算、文件读写等工具")
    print(f"     4. 自我反思：检查结果完整性并修正问题")
    print(f"     5. 最终交付：输出完整的、结构化的周报成果")

    print(f"\n   📊 数据对比：")
    print(f"     普通模型：1 次回答 | 0 次工具调用 | 0 次纠错 | 无自我意识")
    print(f"     AI Agent：{agent.llm.call_count} 次推理 | "
          f"{len(agent.memory.working_memory['tool_results'])} 次工具调用 | "
          f"{len(agent.memory.recall('past_errors'))} 次纠错 | 全流程闭环")

    return chat, agent


# =========================================================================
#  第五部分：6 个应用场景模拟
#  覆盖文中提到的全部主流落地场景
# =========================================================================

def demo_scenario_workplace():
    """场景1：职场自动化Agent —— 自动生成工作周报"""
    print("\n" + "█" * 70)
    print("█  场景1：职场自动化 Agent")
    print("█  自动整理工作记录、生成周报、标注未完成")
    print("█" * 70)

    agent = AIAgentCore("职场自动化Agent")
    return agent.run_complete("【职场日报】请根据本周工作内容生成标准周报")


def demo_scenario_knowledge():
    """场景2：私有知识库Agent —— 基于本地文档精准答疑"""
    print("\n" + "█" * 70)
    print("█  场景2：私有知识库 Agent")
    print("█  导入企业文档/产品手册，搭建专属问答助手")
    print("█" * 70)

    agent = AIAgentCore("知识库Agent")

    # 模拟知识库构建
    agent.memory.remember("knowledge_base", {
        "total_docs": 12,
        "categories": ["产品手册", "技术规范", "FAQ", "操作指南"],
        "last_updated": time.strftime("%Y-%m-%d")
    })

    print(f"\n📚 知识库已加载：{agent.memory.recall('knowledge_base')}")

    question = "【知识库问答】如何配置产品的基础参数？"
    agent.set_goal(question)
    agent.plan()
    agent.execute_plan()
    reflection = agent.self_reflection()
    agent.iterate(reflection)

    return "\n✅ 知识库Agent 完成精准答疑，不依赖大模型训练数据过时问题。"


def demo_scenario_data_analysis():
    """场景3：智能数据分析Agent —— 自动分析Excel数据"""
    print("\n" + "█" * 70)
    print("█  场景3：智能数据分析 Agent")
    print("█  自主读取Excel、数据清洗、趋势分析、输出报告")
    print("█" * 70)

    agent = AIAgentCore("数据分析Agent")
    return agent.run_complete("【数据分析】请分析第一季度销售数据，给出趋势结论")


def demo_scenario_research():
    """场景4：全网调研Agent —— 自动搜索整理调研报告"""
    print("\n" + "█" * 70)
    print("█  场景4：全网调研 Agent")
    print("█  自主联网搜索、筛选去重、结构化输出调研报告")
    print("█" * 70)

    agent = AIAgentCore("调研Agent")
    return agent.run_complete("【全网调研】AI Agent行业最新动态和市场趋势")


def demo_scenario_content():
    """场景5：内容创作Agent —— 多智能体协作批量创作"""
    print("\n" + "█" * 70)
    print("█  场景5：内容创作 Agent")
    print("█  选题→大纲→初稿→润色→排版，全流程自动化")
    print("█" * 70)

    agent = AIAgentCore("内容创作Agent")
    return agent.run_complete("【内容创作】写一篇关于AI Agent的科普文章")


def demo_scenario_personal_assistant():
    """场景6：专属私人助手Agent —— 个性化长期服务"""
    print("\n" + "█" * 70)
    print("█  场景6：专属私人助手 Agent")
    print("█  定制人设、长期记忆、个性化服务")
    print("█" * 70)

    agent = AIAgentCore("私人助手Agent")

    # 模拟长期记忆积累
    agent.memory.remember("user_name", "小明")
    agent.memory.remember("user_preferences", {
        "study_time": "20:00-22:00",
        "interest": "AI Agent开发",
        "learning_pace": "中等",
        "current_level": "初级"
    })
    agent.memory.remember("key_decisions", [
        "决定全职学习AI Agent开发",
        "目标3个月内完成从入门到实战",
    ])

    print(f"\n👤 用户画像已加载：")
    prefs = agent.memory.recall("user_preferences")
    for k, v in prefs.items():
        print(f"    {k}: {v}")

    return agent.run_complete("【私人助手】请根据我的学习进度，给出本周学习建议")


# =========================================================================
#  第六部分：核心差异表 —— 6 维度对比
#  以代码可执行方式呈现文章核心差异表
# =========================================================================

def demo_comparison_table():
    """以代码 + 表格形式呈现核心差异表的 6 个维度"""
    print("\n" + "█" * 70)
    print("█  核心差异表：普通大模型 vs AI Agent（6 维度）")
    print("█" * 70)

    dims = [
        {
            "dim": "运行逻辑",
            "llm": "被动响应，单次问答，无持续任务链路",
            "agent": "主动驱动，目标导向，全流程闭环执行",
            "demo": (
                "LLM: 用户问→AI答→结束\n"
                "Agent: 设定目标→自主规划→执行→反思→迭代→交付"
            )
        },
        {
            "dim": "任务处理",
            "llm": "只擅长简单、碎片化问题",
            "agent": "擅长复杂、多步骤、长流程落地任务",
            "demo": (
                "LLM: 「给我写一首诗」→ 一次性输出\n"
                "Agent: 「帮我完成市场调研」→ 搜索→整理→分析→报告→校验"
            )
        },
        {
            "dim": "工具能力",
            "llm": "原生无工具联动，无法自主调用外部能力",
            "agent": "原生支持工具调用，可联网/计算/操作文件/查数据库",
            "demo": (
                "LLM: 只能基于训练数据回答过时知识\n"
                "Agent: 可调用 web_search / calculator / read_file / query_database"
            )
        },
        {
            "dim": "记忆能力",
            "llm": "仅依赖上下文窗口，无长期记忆、无沉淀",
            "agent": "三级记忆架构：短期+长期+工作记忆，可检索迭代",
            "demo": (
                "LLM: 每次对话从零开始，超过上下文长度丢失\n"
                "Agent: 可长期记住用户偏好、历史错误、关键决策"
            )
        },
        {
            "dim": "纠错能力",
            "llm": "输出即结束，不会自查、不会修正错误",
            "agent": "自我反思、结果校验、迭代优化持续改进",
            "demo": (
                "LLM: 回答错误→用户指正→重新输出（仍需用户发现）\n"
                "Agent: 自动检查结果质量→发现问题→自动修正→再检查"
            )
        },
        {
            "dim": "落地价值",
            "llm": "辅助咨询、文案改写、简单答疑",
            "agent": "自动化办公、业务落地、数据处理、项目调研",
            "demo": (
                "LLM: 适合单次信息查询、内容润色\n"
                "Agent: 可替代重复性工作，实现全流程自动化"
            )
        },
    ]

    # 表格输出
    header = (
        f"\n{'对比维度':<12} | {'普通大模型对话':<30} | {'AI Agent 智能体':<36}"
    )
    sep = "-" * 80
    print(header)
    print(sep)

    for d in dims:
        row = f"{d['dim']:<12} | {d['llm']:<30} | {d['agent']:<36}"
        print(row)
        print(sep)

    # 交互式验证
    print("\n" + "─" * 70)
    print("🔬 【交互验证】每个维度通过代码验证：")
    print("─" * 70)

    for d in dims:
        print(f"\n▸ {d['dim']}")
        print(f"   普通大模型：{d['llm']}")
        print(f"   AI Agent：  {d['agent']}")
        print(f"   代码体现：")
        for line in d['demo'].split('\n'):
            print(f"     {line.strip()}")

    print("\n" + "─" * 70)
    print("💡 结论：普通大模型与AI Agent有本质区别，")
    print("   AI落地的核心竞争力是『设计开发AI Agent』而非『会用AI聊天』。")
    print("─" * 70 + "\n")

    return dims


# =========================================================================
#  第七部分：Agent 四个核心特质独立演示
#  单独展示每一个特质的作用
# =========================================================================

def demo_four_core_traits():
    """独立演示 Agent 的四个核心特质"""

    print("\n" + "█" * 70)
    print("█  AI Agent 四个核心特质独立演示")
    print("█" * 70)

    traits = [
        {
            "name": "① 自主目标意识",
            "description": "不需要人类逐指令指挥，给定最终目标即可自主推进",
            "demo": lambda: _demo_trait_autonomy(),
        },
        {
            "name": "② 任务拆解规划",
            "description": "面对复杂任务自动拆分为有序子任务",
            "demo": lambda: _demo_trait_planning(),
        },
        {
            "name": "③ 工具联动执行",
            "description": "自主调用联网/计算/文件/数据库等外部工具",
            "demo": lambda: _demo_trait_tools(),
        },
        {
            "name": "④ 记忆迭代优化",
            "description": "记住历史、自我反思、迭代修正、越用越精准",
            "demo": lambda: _demo_trait_memory(),
        },
    ]

    for t in traits:
        print(f"\n{'─' * 60}")
        print(f"✦ {t['name']}")
        print(f"  {t['description']}")
        print(f"{'─' * 60}")
        t["demo"]()
        print()

    return traits


def _demo_trait_autonomy():
    """演示自主目标意识"""
    print(f"\n  普通模式需要：用户每步都发指令")
    print(f"    → 「帮我查资料」「帮我整理」「帮我输出」")
    print(f"\n  Agent 模式只需要：给定一个最终目标")
    print(f"    → 「帮我完成一份市场调研报告」")
    print(f"\n  Agent 会自动推进：")
    print(f"    Step 1: 理解目标")
    print(f"    Step 2: 制定执行计划")
    print(f"    Step 3: 逐步执行")
    print(f"    Step 4: 交付结果")

    agent = AIAgentCore("展示-Agent")
    result = agent.run_complete(
        "【规划】做一个简单的信息收集和总结任务"
    )
    print(f"\n  ▶ 结果：Agent 从「给定目标」到「交付结果」全自动完成")
    print(f"  ▶ 中间不需要人工干预")


def _demo_trait_planning():
    """演示任务拆解规划"""
    agent = AIAgentCore("展示-规划器")
    steps = agent.planner.decompose("完成一份竞品分析报告")
    print(f"\n  面对「完成竞品分析报告」这个复杂任务：")
    print(f"  普通大模型 → 直接输出一段笼统的文字")
    print(f"  AI Agent → 拆解为以下有序子任务：")
    for s in steps:
        print(f"     📍 第{s['step']}步：{s['action']} — {s['detail']}")
    print(f"\n  ▶ 每个子任务可独立执行、独立校验")
    print(f"  ▶ 大模型只能整体输出，Agent 能分步落地")


def _demo_trait_tools():
    """演示工具联动执行"""
    print(f"\n  普通大模型能力边界：")
    print(f"    ❌ 不能联网获取最新信息")
    print(f"    ❌ 不能计算复杂表达式")
    print(f"    ❌ 不能读写本地文件")
    print(f"    ❌ 不能操作数据库")
    print(f"\n  AI Agent 工具联动：")
    print(f"    ✅ 能调用 web_search 获取实时信息")
    print(f"    ✅ 能调用 calculator 执行精确计算")
    print(f"    ✅ 能调用 read_file 读取Excel/Word/PDF")
    print(f"    ✅ 能调用 query_database 查询数据库")
    print(f"    ✅ 能调用 excel_analyze 分析数据")

    tools = ToolRegistry()
    print(f"\n  演示工具调用：")
    print(f"    web_search('AI Agent 2025')")
    print(f"    → {tools.web_search('AI Agent 2025')}")
    print(f"    calculator('(1250 + 3800) * 2')")
    print(f"    → {tools.calculator('(1250 + 3800) * 2')}")
    print(f"    read_file('sales_data.xlsx')")
    print(f"    → {tools.read_file('sales_data.xlsx')}")
    print(f"    excel_analyze('sales_data.xlsx')")
    print(f"    → {tools.excel_analyze('sales_data.xlsx')}")
    print(f"\n  ▶ Agent 通过工具联动，突破了大模型本身的能力天花板")


def _demo_trait_memory():
    """演示记忆与迭代优化"""
    print(f"\n  普通大模型的记忆问题：")
    print(f"    ❌ 超过上下文窗口就遗忘")
    print(f"    ❌ 每次对话从零开始")
    print(f"    ❌ 不会从错误中学习")
    print(f"\n  AI Agent 三级记忆架构：")
    print(f"    Level 1 - 短期记忆：当前对话上下文")
    print(f"    Level 2 - 长期记忆：用户偏好/历史信息/关键决策")
    print(f"    Level 3 - 工作记忆：任务中间状态/工具结果/执行进度")

    memory = MemorySystem()
    memory.add("user", "我喜欢简洁的风格")
    memory.add("agent", "已记录用户风格偏好")
    memory.remember("user_preferences", {"style": "简洁"})
    memory.mark_error("第2部分数据字段遗漏")
    memory.mark_error("输出格式未对齐")

    print(f"\n  演示记忆能力：")
    print(f"    短期记忆：{memory.get_context(3)}")
    print(f"    长期记忆偏好：{memory.recall('user_preferences')}")
    print(f"    已记录错误：{len(memory.recall('past_errors'))} 次")
    print(f"    记忆摘要：{memory.summarize()}")

    print(f"\n  演示反思迭代：")
    agent = AIAgentCore("展示-记忆")
    agent.memory = memory
    reflection = agent.self_reflection()
    agent.iterate(reflection)
    print(f"\n  ▶ Agent 越用越精准，不会每次从零开始")


# =========================================================================
#  第八部分：main 入口 —— 运行全部演示
# =========================================================================

def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   《AI Agent 零基础实战》第1篇 · 配套完整演示代码                   ║
║                                                                    ║
║   AI Agent 到底是什么？                                            ║
║   告别玄学，一文读懂智能体的本质                                   ║
║                                                                    ║
║   覆盖内容：                                                       ║
║   ✅ 普通大模型 vs AI Agent 对比演示                               ║
║   ✅ Agent 四个核心特质（自主/规划/工具/记忆）                     ║
║   ✅ 6 个应用场景模拟                                              ║
║   ✅ 核心差异表 6 维度对比                                         ║
║                                                                    ║
║   模拟后端，无需 API Key，直接运行                                 ║
║                                                                    ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main_menu():
    """主菜单 —— 让用户选择要运行的部分"""
    print("\n" + "=" * 70)
    print("请选择要运行的演示模块：")
    print("=" * 70)
    print("  [0] 运行全部演示（完整流程）")
    print("  [1] 普通大模型 vs AI Agent 对比演示")
    print("  [2] Agent 四个核心特质独立演示")
    print("  [3] 场景1：职场自动化 Agent")
    print("  [4] 场景2：私有知识库 Agent")
    print("  [5] 场景3：智能数据分析 Agent")
    print("  [6] 场景4：全网调研 Agent")
    print("  [7] 场景5：内容创作 Agent")
    print("  [8] 场景6：专属私人助手 Agent")
    print("  [9] 核心差异表 6 维度对比")
    print("  [q] 退出")
    print("-" * 70)

    choice = input("请输入选项 (0-9, q): ").strip().lower()

    runners = {
        "0": lambda: (
            print("\n📢 即将运行全部演示，请耐心等待...\n"),
            demo_comparison(),
            demo_four_core_traits(),
            demo_scenario_workplace(),
            demo_scenario_knowledge(),
            demo_scenario_data_analysis(),
            demo_scenario_research(),
            demo_scenario_content(),
            demo_scenario_personal_assistant(),
            demo_comparison_table(),
        ),
        "1": demo_comparison,
        "2": demo_four_core_traits,
        "3": demo_scenario_workplace,
        "4": demo_scenario_knowledge,
        "5": demo_scenario_data_analysis,
        "6": demo_scenario_research,
        "7": demo_scenario_content,
        "8": demo_scenario_personal_assistant,
        "9": demo_comparison_table,
    }

    if choice == "q":
        print("👋 感谢阅读！下次再见。")
        return False

    runner = runners.get(choice)
    if runner:
        runner()
    else:
        print("❌ 无效输入，请输入 0-9 或 q")

    return True


def run_all_demo():
    """自动运行全部演示（非交互模式）"""
    print_banner()

    print("\n" + "═" * 70)
    print("  第一部分：普通大模型 vs AI Agent 对比演示")
    print("═" * 70)
    demo_comparison()

    print("\n" + "═" * 70)
    print("  第二部分：Agent 四个核心特质独立演示")
    print("═" * 70)
    demo_four_core_traits()

    print("\n" + "═" * 70)
    print("  第三部分：6 个应用场景模拟")
    print("═" * 70)
    demo_scenario_workplace()
    demo_scenario_knowledge()
    demo_scenario_data_analysis()
    demo_scenario_research()
    demo_scenario_content()
    demo_scenario_personal_assistant()

    print("\n" + "═" * 70)
    print("  第四部分：核心差异表 6 维度对比")
    print("═" * 70)
    demo_comparison_table()

    print("\n" + "⭐" * 35)
    print("🎉 全部演示完成！")
    print("⭐" * 35)
    print("\n📖 配套文章：《第1篇：AI Agent到底是什么？》")
    print("💻 本文件：01_agent_full_demo.py")
    print("📁 位置：01-AI-Agent到底是什么/code/")
    print("\n💡 提示：运行 python 01_agent_full_demo.py 可进入交互菜单模式")


if __name__ == "__main__":
    import sys

    print_banner()

    # 命令行参数：--all 直接运行全部
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_all_demo()
    else:
        print("💡 运行模式说明：")
        print("   python 01_agent_full_demo.py        → 交互菜单模式")
        print("   python 01_agent_full_demo.py --all  → 自动运行全部\n")

        while True:
            try:
                if not main_menu():
                    break
                again = input("\n🔄 是否返回主菜单继续体验？(y/n): ").strip().lower()
                if again != "y":
                    print("👋 感谢阅读！下次再见。")
                    break
            except KeyboardInterrupt:
                print("\n\n👋 已退出。感谢阅读！")
                break
            except EOFError:
                print("\n\n👋 已退出。感谢阅读！")
                break
