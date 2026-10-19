#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第7篇配套完整演示代码
AI Agent开发框架选型与对比（新手最优落地方案）
==========================================================================

本文件为《AI Agent 零基础实战》第7篇的配套完整项目代码。
完全基于文章内容编写，覆盖文中全部技术点，使用模拟实现，可直接运行。

运行方式: python 01_framework_selection_full.py
"""

from typing import Dict, List, Optional


# ======================================================================
# 第一部分：五大主流框架的完整信息模型
# ======================================================================

class FrameworkInfo:
    """框架信息模型"""
    
    def __init__(self, name: str, positioning: str, strengths: List[str],
                 weaknesses: List[str], scenarios: List[str],
                 beginner_rating: int, labels: List[str]):
        self.name = name
        self.positioning = positioning
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.scenarios = scenarios
        self.beginner_rating = beginner_rating
        self.labels = labels
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "positioning": self.positioning,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "scenarios": self.scenarios,
            "beginner_rating": self.beginner_rating,
            "labels": self.labels,
        }


# 五大框架的完整信息
FRAMEWORKS: Dict[str, FrameworkInfo] = {
    "LangChain/LangGraph": FrameworkInfo(
        name="LangChain/LangGraph",
        positioning="全能通用型开发框架——生态最完善、通用性最强的全场景Agent开发底座",
        strengths=[
            "生态最全：适配所有大模型、向量库、工具接口，无兼容壁垒",
            "能力完整：原生支持规划、记忆、工具、反思、状态管理",
            "可落地性强：支持循环、分支、断点续跑、人工介入，适配工业级项目",
            "调试完善：配套 LangSmith 可视化调试，快速排查报错",
        ],
        weaknesses=[
            "早期版本封装冗余，新手容易看不懂底层逻辑",
            "复杂项目代码量偏大，需要一定基础沉淀",
        ],
        scenarios=["办公自动化Agent", "流程化任务Agent", "工具调用型智能体", "商用定制项目"],
        beginner_rating=5,
        labels=["主力必学", "全场景通用", "商用首选"],
    ),
    "LlamaIndex": FrameworkInfo(
        name="LlamaIndex",
        positioning="数据检索专属框架——RAG知识库与文档检索天花板",
        strengths=[
            "文档处理能力极强：支持130+文件格式，内置精细化解析、分块、索引策略",
            "检索精度更高：混合检索、递归检索、权重排序原生支持",
            "开箱即用：少量代码即可搭建高精度私有知识库Agent",
        ],
        weaknesses=[
            "通用流程编排能力弱于 LangChain",
            "非RAG场景性价比低，不适合纯工具执行、多流程任务",
        ],
        scenarios=["企业知识库", "私有文档问答", "PDF/Word资料智能助手", "本地知识库检索"],
        beginner_rating=4,
        labels=["专项必学", "RAG天花板", "知识库首选"],
    ),
    "AutoGPT": FrameworkInfo(
        name="AutoGPT",
        positioning="全自动任务执行框架——目标驱动的全自动黑盒Agent",
        strengths=[
            "上手极快，零代码/少代码即可运行全自动任务",
            "原生自带自主规划、循环执行、多轮迭代能力",
        ],
        weaknesses=[
            "高度黑盒，底层逻辑封闭，无法深度定制",
            "任务随机性强、稳定性差，极易跑偏",
            "不支持精细化调试，完全无法商用落地",
        ],
        scenarios=["个人趣味体验", "简单调研任务", "新手认知学习"],
        beginner_rating=2,
        labels=["仅体验", "黑盒不可控", "不推荐深耕"],
    ),
    "CrewAI": FrameworkInfo(
        name="CrewAI",
        positioning="轻量化多智能体框架——极简多角色Agent协作框架",
        strengths=[
            "语法极简、代码量极少，新手极易上手",
            "角色分工清晰：研究员、文案、审核、分析师各司其职",
            "天然适配流水线、批量内容生产、多步骤协作任务",
        ],
        weaknesses=[
            "复杂流程、精细控制能力不如 LangGraph",
            "生态相对轻量化，高阶拓展较少",
        ],
        scenarios=["自媒体批量创作", "团队式AI协作", "调研分析流水线", "轻量化多Agent项目"],
        beginner_rating=4,
        labels=["轻量化多Agent首选", "流水线协作", "极简上手"],
    ),
    "AutoGen": FrameworkInfo(
        name="AutoGen",
        positioning="老牌多智能体框架——微软出品的多Agent对话协作框架，主打多角色对话交互",
        strengths=[
            "多角色对话逻辑成熟",
        ],
        weaknesses=[
            "目前处于维护模式，迭代缓慢",
            "上手偏复杂、代码冗余",
            "对比 CrewAI 没有新手优势，新项目基本不再首选",
        ],
        scenarios=["老旧项目维护"],
        beginner_rating=2,
        labels=["不推荐新手", "迭代停滞", "性价比低"],
    ),
}


# ======================================================================
# 第二部分：选型规则引擎
# ======================================================================

class FrameworkSelector:
    """框架选型规则引擎 - 先场景、后选型"""
    
    # 场景 → 推荐框架映射（依据文章第四章）
    SCENE_MAPPING = {
        "办公自动化": ("LangChain/LangGraph", "流程编排、工具调用、状态管理"),
        "流程化任务": ("LangChain/LangGraph", "复杂任务闭环、断点续跑"),
        "工具调用型智能体": ("LangChain/LangGraph", "工具调用、反射、状态管理"),
        "商用定制项目": ("LangChain/LangGraph", "可定制、可商用、生态全"),
        "企业知识库": ("LlamaIndex", "文档解析、RAG检索天花板"),
        "私有文档问答": ("LlamaIndex", "130+格式解析、精准检索"),
        "PDF/Word资料助手": ("LlamaIndex", "内置分块、索引策略"),
        "本地知识库检索": ("LlamaIndex", "混合检索、递归检索"),
        "自媒体批量创作": ("CrewAI", "角色分工、流水线批量内容生产"),
        "多角色AI协作": ("CrewAI", "极简多Agent分工"),
        "调研分析流水线": ("CrewAI", "流水线任务、角色各司其职"),
        "全自动任务体验": ("AutoGPT", "零代码体验全自动效果"),
        "个人趣味体验": ("AutoGPT", "快速体验智能体效果"),
    }
    
    def recommend(self, scene: str) -> Dict:
        """根据场景推荐框架"""
        # 精确匹配
        if scene in self.SCENE_MAPPING:
            framework, reason = self.SCENE_MAPPING[scene]
            return {"scene": scene, "framework": framework, "reason": reason}
        
        # 模糊匹配
        for key, (framework, reason) in self.SCENE_MAPPING.items():
            if key in scene or scene in key:
                return {"scene": scene, "framework": framework, "reason": reason}
        
        # 默认推荐
        return {"scene": scene, "framework": "LangChain/LangGraph", "reason": "通用全场景默认推荐"}
    
    def recommend_by_role(self, role: str, budget: Optional[str] = None) -> Dict:
        """按用户角色推荐（个人开发/副业变现/企业项目）"""
        role_map = {
            "个人开发": {
                "main": "LangChain/LangGraph",
                "specialty": "LlamaIndex",
                "lightweight": "CrewAI",
                "avoid": ["AutoGPT", "AutoGen"],
            },
            "副业变现": {
                "main": "LangChain/LangGraph",
                "specialty": "LlamaIndex",
                "lightweight": "CrewAI",
                "avoid": ["AutoGPT", "AutoGen"],
            },
            "企业项目": {
                "main": "LangChain/LangGraph",
                "specialty": "LlamaIndex",
                "lightweight": "CrewAI（批量内容）",
                "avoid": ["AutoGen（仅老项目维护）"],
            },
        }
        return role_map.get(role, role_map["个人开发"])


# ======================================================================
# 第三部分：模拟 LangChain 风格实现
# ======================================================================

class SimpleChain:
    """极简模拟 LangChain 链式调用"""
    
    def __init__(self):
        self.steps: List[Dict] = []
    
    def add_step(self, name: str, func):
        """添加链式步骤"""
        self.steps.append({"name": name, "func": func})
        return self
    
    def invoke(self, input_data: Dict) -> Dict:
        """执行链式调用"""
        print(f"\n🔗 执行LangChain风格链式调用（{len(self.steps)}步）")
        data = input_data
        for step in self.steps:
            print(f"  ▶ {step['name']}")
            data = step["func"](data)
            print(f"    → 输出: {str(data)[:80]}")
        return data


class SimpleToolChain:
    """极简模拟 LangChain 工具链"""
    
    def __init__(self):
        self.tools: Dict[str, callable] = {}
    
    def register_tool(self, name: str, func):
        self.tools[name] = func
    
    def run_with_tool(self, task: str) -> Dict:
        print(f"\n🛠️ LangChain工具链模式：{task}")
        # 模拟工具选择
        if "搜索" in task or "资料" in task:
            tool = "web_search"
            result = self.tools.get(tool, lambda x: f"搜索结果: {x}")(task)
        elif "计算" in task or "算" in task:
            tool = "calculator"
            result = self.tools.get(tool, lambda x: "计算结果: 300")(task)
        else:
            tool = "answer"
            result = self.tools.get(tool, lambda x: f"回答: {x}")(task)
        return {"tool": tool, "result": result}


# ======================================================================
# 第四部分：模拟 LlamaIndex 风格实现
# ======================================================================

class SimpleDocumentIndex:
    """极简模拟 LlamaIndex 文档索引"""
    
    def __init__(self):
        self.documents: List[Dict] = []
        self.chunks: List[Dict] = []
    
    def load_document(self, name: str, content: str):
        """加载文档"""
        self.documents.append({"name": name, "content": content})
        print(f"  📄 加载文档: {name}（{len(content)}字）")
    
    def split_into_chunks(self, chunk_size: int = 100):
        """分块（LlamaIndex 的核心能力之一）"""
        for doc in self.documents:
            content = doc["content"]
            for i in range(0, len(content), chunk_size):
                self.chunks.append({
                    "doc": doc["name"],
                    "chunk": content[i:i+chunk_size],
                    "index": len(self.chunks)
                })
        print(f"  ✂️ 文档分块完成：{len(self.chunks)}个块")
    
    def build_index(self):
        """构建索引（模拟向量索引）"""
        # 模拟：用关键词建立倒排索引
        self.index = {}
        for chunk in self.chunks:
            for word in chunk["chunk"]:
                self.index.setdefault(word, []).append(chunk["index"])
        print(f"  🗂️ 索引构建完成（{len(self.index)}个关键词）")
    
    def query(self, question: str, top_k: int = 3) -> List[Dict]:
        """检索 - 混合检索模拟"""
        print(f"\n🔍 LlamaIndex检索模式：{question}")
        # 简单关键词匹配
        matched = []
        for chunk in self.chunks:
            score = sum(1 for ch in question if ch in chunk["chunk"])
            if score > 0:
                matched.append((score, chunk))
        matched.sort(key=lambda x: x[0], reverse=True)
        results = [c for _, c in matched[:top_k]]
        print(f"  📊 召回 {len(results)} 个相关片段")
        for r in results:
            print(f"    [{r['index']}] {r['chunk'][:50]}...")
        return results


# ======================================================================
# 第五部分：模拟 CrewAI 风格实现
# ======================================================================

class CrewAgent:
    """CrewAI 角色Agent"""
    
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory
    
    def execute_task(self, task: str) -> str:
        """执行任务"""
        print(f"  👤 [{self.role}] 正在执行：{task}")
        result = f"[{self.role}完成] {task}的结果（基于目标：{self.goal}）"
        print(f"    ✅ {result[:60]}")
        return result


class SimpleCrew:
    """CrewAI 多Agent协作组"""
    
    def __init__(self):
        self.agents: List[CrewAgent] = []
        self.tasks: List[Dict] = []
    
    def add_agent(self, agent: CrewAgent):
        self.agents.append(agent)
    
    def add_task(self, description: str, agent: CrewAgent):
        self.tasks.append({"description": description, "agent": agent})
    
    def kickoff(self) -> str:
        """启动协作（流水线模式）"""
        print(f"\n🚀 CrewAI 多Agent协作启动（{len(self.agents)}个角色，{len(self.tasks)}个任务）")
        print("=" * 55)
        results = []
        context = ""
        for i, task in enumerate(self.tasks, 1):
            print(f"\n📌 任务{i}: {task['description']}")
            result = task["agent"].execute_task(task["description"] + (" | 上下文:" + context if context else ""))
            results.append(result)
            context = result[:50]
        print("\n" + "=" * 55)
        print("🎉 CrewAI 协作完成！")
        return "\n".join(results)


# ======================================================================
# 第六部分：框架组合演示（商用最优方案）
# ======================================================================

class CombinedFrameworkDemo:
    """商用级框架组合演示
    主体流程：LangGraph → 数据检索：LlamaIndex → 多Agent：CrewAI
    """
    
    def run(self):
        print("\n" + "=" * 70)
        print("          🏗️ 商用级框架组合方案演示")
        print("          LangGraph(流程) + LlamaIndex(检索) + CrewAI(协作)")
        print("=" * 70)
        
        # 1. LangGraph 负责流程编排
        print("\n" + "-" * 60)
        print("【1】LangGraph 流程编排层")
        print("-" * 60)
        chain = SimpleChain()
        chain.add_step("接收任务", lambda d: {**d, "task": d.get("task", "")})
        chain.add_step("拆解规划", lambda d: {**d, "plan": "拆成: 检索→分析→写稿→审核"})
        chain.add_step("状态检查", lambda d: {**d, "status": "ready"})
        state = chain.invoke({"task": "生成AI行业研究简报"})
        
        # 2. LlamaIndex 负责知识检索
        print("\n" + "-" * 60)
        print("【2】LlamaIndex 知识检索层")
        print("-" * 60)
        index = SimpleDocumentIndex()
        index.load_document("AI行业报告2024", "AI Agent市场规模2024年达到100亿美元，同比增长45%。RAG技术显著降低幻觉，被企业广泛采用。多模态成为新趋势。")
        index.load_document("竞品分析", "LangChain生态最全，LlamaIndex检索最强，CrewAI多Agent最简。")
        index.split_into_chunks(chunk_size=60)
        index.build_index()
        retrieved = index.query("AI Agent市场规模", top_k=2)
        
        # 3. CrewAI 多Agent协作
        print("\n" + "-" * 60)
        print("【3】CrewAI 多Agent协作层")
        print("-" * 60)
        crew = SimpleCrew()
        researcher = CrewAgent("研究员", "搜集并整理资料", "资深行业研究员")
        analyst = CrewAgent("分析师", "分析数据得出结论", "数据分析专家")
        writer = CrewAgent("文案", "撰写可读性强的简报", "资深内容创作者")
        reviewer = CrewAgent("审核", "检查内容质量", "严格的质量审核专家")
        
        crew.add_agent(researcher)
        crew.add_agent(analyst)
        crew.add_agent(writer)
        crew.add_agent(reviewer)
        
        crew.add_task("检索AI行业最新数据", researcher)
        crew.add_task("分析市场规模与趋势", analyst)
        crew.add_task("撰写行业简报", writer)
        crew.add_task("审核简报质量", reviewer)
        crew.kickoff()
        
        print("\n" + "=" * 70)
        print("✅ 组合完成：流程可控(LangGraph) + 检索精准(LlamaIndex) + 协作高效(CrewAI)")
        print("=" * 70)


# ======================================================================
# 第七部分：主程序
# ======================================================================

def demo_framework_overview():
    """展示五大框架全景"""
    print("\n" + "=" * 70)
    print("          📊 五大主流AI Agent框架全景对比")
    print("=" * 70)
    
    for name, fw in FRAMEWORKS.items():
        stars = "⭐" * fw.beginner_rating
        print(f"\n{'─' * 62}")
        print(f"🔷 {name}  {stars}")
        print(f"  定位：{fw.positioning}")
        print(f"  标签：{' / '.join(fw.labels)}")
        print(f"  优势：")
        for s in fw.strengths:
            print(f"    ✅ {s}")
        print(f"  短板：")
        for w in fw.weaknesses:
            print(f"    ⚠️ {w}")
        print(f"  最佳场景：{' / '.join(fw.scenarios)}")


def demo_selection():
    """演示选型规则引擎"""
    print("\n" + "=" * 70)
    print("          🎯 场景选型推荐")
    print("=" * 70)
    
    selector = FrameworkSelector()
    
    scenes = ["办公自动化", "企业知识库", "自媒体批量创作", "全自动任务体验", "商用定制项目"]
    for scene in scenes:
        rec = selector.recommend(scene)
        print(f"\n  📌 场景：{scene}")
        print(f"     推荐：{rec['framework']}")
        print(f"     理由：{rec['reason']}")
    
    print("\n" + "-" * 60)
    print("按用户角色推荐：")
    for role in ["个人开发", "副业变现", "企业项目"]:
        rec = selector.recommend_by_role(role)
        print(f"\n  👤 {role}")
        print(f"     主力：{rec['main']}")
        print(f"     专项：{rec['specialty']}")
        print(f"     轻量：{rec['lightweight']}")
        print(f"     避坑：{'、'.join(rec['avoid'])}")


def demo_langchain():
    """演示 LangChain 风格"""
    print("\n" + "=" * 70)
    print("          🔗 LangChain 风格：链式调用 + 工具链")
    print("=" * 70)
    
    # 链式调用
    chain = SimpleChain()
    chain.add_step("接收用户输入", lambda d: {**d, "user_input": "帮我生成一份周报"})
    chain.add_step("任务规划", lambda d: {**d, "plan": ["收集数据", "生成内容", "检查质量"]})
    chain.add_step("执行规划", lambda d: {**d, "output": "周报已生成"})
    chain.invoke({"initial": True})
    
    # 工具链
    chain2 = SimpleToolChain()
    chain2.register_tool("web_search", lambda x: f"🔍 搜索结果：关于'{x}'的最新信息...")
    chain2.register_tool("calculator", lambda x: "🧮 计算结果：1,200,000")
    chain2.run_with_tool("搜索AI行业最新资料")
    chain2.run_with_tool("计算本季度销售额")


def demo_llamaindex():
    """演示 LlamaIndex 风格"""
    print("\n" + "=" * 70)
    print("          📚 LlamaIndex 风格：文档索引 + 检索")
    print("=" * 70)
    
    index = SimpleDocumentIndex()
    index.load_document(
        "企业产品手册",
        "我们的AI客服系统支持多轮对话、知识库问答、工具调用。"
        "支持私有化部署，数据不出内网。核心优势是低幻觉、可溯源。"
        "已在金融、医疗、制造三个行业落地。"
    )
    index.load_document(
        "技术白皮书",
        "基于RAG架构，使用混合检索+重排序提升准确率。"
        "向量库使用ChromaDB，支持增量更新。"
    )
    index.split_into_chunks(chunk_size=50)
    index.build_index()
    
    # 多个查询
    index.query("AI客服系统有哪些能力")
    index.query("部署方式和技术架构")


def demo_crewai():
    """演示 CrewAI 风格"""
    print("\n" + "=" * 70)
    print("          👥 CrewAI 风格：多Agent流水线协作")
    print("=" * 70)
    
    crew = SimpleCrew()
    
    # 定义角色
    roles = [
        CrewAgent("选题策划", "确定内容方向", "资深内容策划"),
        CrewAgent("内容撰写", "完成文章初稿", "资深文案"),
        CrewAgent("润色优化", "提升内容质量", "文字编辑专家"),
        CrewAgent("质量审核", "确保内容准确", "严格审核"),
    ]
    for r in roles:
        crew.add_agent(r)
    
    # 定义流水线任务
    crew.add_task("策划一篇AI工具推荐选题", roles[0])
    crew.add_task("撰写1500字的AI工具推荐文章", roles[1])
    crew.add_task("润色文章，优化表达和结构", roles[2])
    crew.add_task("审核文章的事实准确性和风格", roles[3])
    
    crew.kickoff()


def demo_recommendation_path():
    """新手学习路线推荐"""
    print("\n" + "=" * 70)
    print("          🗺️ 2026 新手学习路径（直接照搬）")
    print("=" * 70)
    
    path = [
        ("第1阶段：入门主力", "LangChain + LangGraph", "搞定90%个人/副业/企业Agent项目，长期保值"),
        ("第2阶段：专项能力", "LlamaIndex", "攻克知识库、私有文档、RAG检索场景"),
        ("第3阶段：轻量协作", "CrewAI", "快速实现多AI分工协作、批量内容生产"),
        ("不学", "AutoGPT、AutoGen、老旧框架", "浪费学习时间，无落地价值"),
    ]
    
    for stage, target, reason in path:
        print(f"\n  🎯 {stage}")
        print(f"     学习：{target}")
        print(f"     原因：{reason}")
    
    print("\n" + "-" * 60)
    print("三大避坑要点：")
    print("  1. 不要同时学多个框架（先LangChain → LlamaIndex → CrewAI）")
    print("  2. 不要沉迷框架玄学（核心是前6篇的底层架构思维）")
    print("  3. 学框架一定要落地项目（每学一个模块就做一个小项目）")


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       🧭 AI Agent 框架选型与对比 - 完整配套演示代码         ║
║       《AI Agent 零基础实战》第7篇                          ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    while True:
        print("\n" + "─" * 60)
        print("请选择演示模式：")
        print("1. 五大框架全景对比")
        print("2. 场景选型推荐引擎")
        print("3. LangChain 风格演示（链式+工具）")
        print("4. LlamaIndex 风格演示（索引+检索）")
        print("5. CrewAI 风格演示（多Agent协作）")
        print("6. 商用级框架组合方案")
        print("7. 新手学习路径推荐")
        print("8. 全部运行")
        print("0. 退出")
        print("─" * 60)
        
        choice = input("请输入选项 (0-8): ").strip()
        
        if choice == "1":
            demo_framework_overview()
        elif choice == "2":
            demo_selection()
        elif choice == "3":
            demo_langchain()
        elif choice == "4":
            demo_llamaindex()
        elif choice == "5":
            demo_crewai()
        elif choice == "6":
            CombinedFrameworkDemo().run()
        elif choice == "7":
            demo_recommendation_path()
        elif choice == "8":
            demo_framework_overview()
            demo_selection()
            demo_langchain()
            demo_llamaindex()
            demo_crewai()
            CombinedFrameworkDemo().run()
            demo_recommendation_path()
        elif choice == "0":
            print("感谢使用！")
            break
        else:
            print("无效输入，请重新选择。")


if __name__ == "__main__":
    main()
