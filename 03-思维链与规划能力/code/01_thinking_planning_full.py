# 第3篇完整配套代码：思维链与规划能力
# 覆盖所有技术点：三大缺陷 / CoT / ToT / ReAct / Reflexion / 全自动任务拆解
# 运行：python 01_thinking_planning_full.py

import json
import random
import time

# ====================================================================
# 第一部分：大模型"单次输出"的三大天生缺陷
# ====================================================================
def demonstrate_llm_defects():
    """模拟大模型无规划时的三大致命问题"""
    
    print("=" * 70)
    print("🧩 第一部分：大模型“单次输出”的三大天生缺陷")
    print("=" * 70)

    # ---------- 缺陷1：任务一锅烩，不会拆解 ----------
    print("\n" + "─" * 50)
    print("❌ 缺陷1：任务一锅烩，不会拆解")
    print("  用户输入一个复杂目标，模型试图一次性输出所有内容")
    print("  结果：逻辑混乱、要点缺失、结构崩盘")
    print("─" * 50)

    complex_task = "帮我分析公司第一季度经营情况，包括收入、成本、利润、现金流，"
    complex_task += "对比去年同期，找出异常点，给出改进建议，并生成一份汇报PPT提纲"
    
    # 模拟无规划的LLM输出：一次塞进所有内容，逻辑跳跃
    one_shot_output = """
好的，以下是对公司第一季度经营情况的分析：

收入方面本季度总收入5000万同比去年4500万增长11.1%，
成本方面总成本3500万比去年3200万增加300万主要是人力成本上升，
利润方面毛利润1500万同比1300万增长15.4%，
净利润800万同比700万增长14.3%，
现金流方面经营性现金流1000万同比800万增长25%，
建议控制人力成本，优化采购流程，加强应收账款管理。

关于异常点：毛利率从去年的28.9%下降到30%？？？不对，去年是28.9%今年是30%略有上升，
但管理费用增长了20%需要关注。
改进建议：
1. 控制成本
2. 提升效率
3. 拓展市场

PPT提纲：
封面 - 目录 - 收入分析 - 成本分析 - 利润分析 - 现金流 - 建议 - 结尾
"""
    print("\n  📝 无规划的一次性输出：")
    print(f"  {one_shot_output.strip()[:200]}...")
    print("\n  ⚠️ 问题诊断：")
    print("     • 数据和结论混杂在一起，没有层层递进")
    print("     • 数字出现矛盾（毛利率计算似乎有误且自我否定）")
    print("     • 改进建议只有干巴巴的三条，没有展开")
    print("     • PPT提纲只有标题，没有任何每页的内容要点")
    print("     • 完全看不出分析思路和推导过程")

    # ---------- 缺陷2：无中间推理，细节容易错漏 ----------
    print("\n" + "─" * 50)
    print("❌ 缺陷2：无中间推理，细节容易错漏")
    print("  模型直接输出最终答案，跳过中间思考步骤")
    print("  结果：没有验算、没有推理过程，极易出现逻辑BUG和事实幻觉")
    print("─" * 50)

    calc_task = "一家公司第一季度收入500万，第二季度增长20%，第三季度比第二季度下降10%，第四季度与第三季度持平，全年总收入是多少？"

    # 模拟无推理的错误输出
    wrong_direct_answer = """
全年总收入 = 500 + 600 + 540 + 540 = 2180万
"""
    # 模拟带推理的正确输出
    correct_step_by_step = """
一步一步计算：
第一季度：500万
第二季度：500 × (1 + 20%) = 500 × 1.2 = 600万
第三季度：600 × (1 - 10%) = 600 × 0.9 = 540万
第四季度：与第三季度持平 = 540万
全年总收入 = 500 + 600 + 540 + 540 = 2180万
"""
    print("\n  📝 无推理的直接回答：")
    print(f"     {wrong_direct_answer.strip()}")
    print("     → 结果对了，但你看不到计算过程，无法验证")
    print("     → 如果题目更复杂，没有推理过程就很容易出错")

    print("\n  📝 带推理的分步计算：")
    print(f"     {correct_step_by_step.strip()}")
    print("     → 每一步都清晰可验证")
    print("     → 即使最终结果错了，也能定位到具体哪一步出错")

    # ---------- 缺陷3：无法迭代推进，一步错步步错 ----------
    print("\n" + "─" * 50)
    print("❌ 缺陷3：无法迭代推进，一步错步步错")
    print("  普通问答是“一次性交付”，没有纠错、没有回溯、没有二次优化")
    print("  结果：只要初始判断出错，整段结果全部作废，且系统不会自我修复")
    print("─" * 50)

    print("""
  📝 场景：用户说"帮我写一份产品推广方案"
  
  第1步（初始判断出错）：
    → 模型认为产品是一款低价快消品
    → 所有后续输出都基于这个错误前提
  
  第2步（基于错误前提展开）：
    → 方案定位：适合下沉市场拼多多渠道
    → 定价策略：9.9元低价引流
    → 营销方式：地推+社区团购
  
  第3步（用户反馈）：
    → "这是企业级SaaS产品，客单价5万+"
    → 之前所有内容全部作废，需要重来
  
  问题本质：没有"暂停检查"机制，一次输出后就结束了
  """)

    print("  ✅ 有规划的Agent会先确认前提：")
    print("     "产品推广方案" → 先问清楚产品类型/目标用户/预算")
    print("     → 确认后再展开，避免方向性错误")
    print("     → 每一步都有检查点，发现偏差及时纠正")


# ====================================================================
# 模拟LLM调用（模拟输出不同Prompt的实际效果）
# ====================================================================
def simulate_llm(prompt, mode="naive"):
    """模拟不同模式下的大模型输出，展示效果差异"""
    if mode == "naive":
        return """自媒体新人快速起号的核心是内容质量和持续输出。建议选择你擅长的领域，保持每天更新，多互动，积累粉丝。关键是坚持，没有捷径。"""
    elif mode == "cot":
        return """【分步分析】
1️⃣ 新人起号的核心难点：
   - 没有初始流量积累，曝光困难
   - 没有信任背书，转化率低
   - 赛道竞争激烈，同质化严重

2️⃣ 起号的关键核心要素：
   - 精准定位：细分赛道找到差异化切入点
   - 爆款内容：前5条内容决定账号生死
   - 平台机制：利用推荐算法获得初始流量

3️⃣ 分阶段执行步骤：
   第一阶段（1-7天）：确定定位→研究对标账号→准备10条内容
   第二阶段（8-30天）：日更测试→数据分析→优化内容方向
   第三阶段（31-90天）：稳定更新→互动维护→逐步商业化

4️⃣ 避坑要点：
   - 不要追求完美，先发出去再优化
   - 不要频繁更换定位，至少坚持30天
   - 不要只发不互动，算法重视互动率

【最终建议】
新人起号最稳妥的路径：选择一个细分领域 → 模仿对标账号的爆款模式 → 每天更新1条 → 坚持30天 → 根据数据迭代。"""
    elif mode == "tot":
        return """【ToT多路径推演】

路径A：低成本内容矩阵
  可行性：0.85
  成本：低（时间成本为主）
  策略：制作图文/短视频，利用平台自然流量
  风险评估：竞争激烈，出爆款概率5%-10%
  预计见效时间：30-60天

路径B：投流付费推广
  可行性：0.60
  成本：高（初期至少5000-10000元）
  策略：DOU+/信息流广告，快速获取精准流量
  风险评估：ROI不确定，停止投放后流量下降
  预计见效时间：3-7天

路径C：矩阵号运营
  可行性：0.75
  成本：中（多账号维护成本）
  策略：3-5个账号同步运营，互相导流
  风险评估：平台对矩阵号有限制风险
  预计见效时间：15-30天

路径D：借势热点引流
  可行性：0.70
  成本：低（需随时关注热点）
  策略：紧跟热点话题创作，获取搜索流量
  风险评估：热点时效性短，需要快速响应
  预计见效时间：即时但短暂

【择优结论】
推荐路径：路径A + 路径D 组合
理由：低成本启动，先用热点获取初始关注，再用持续内容留住用户
淘汰路径：路径B（资金有限时不推荐先投流）"""
    elif mode == "react":
        return """Thought: 用户想了解如何快速起号，但"快速"是一个主观概念，我需要先明确用户的具体情况才能给出针对性建议。

Action: ask_user | 你目前是否有自媒体账号？你的目标平台是哪一个？每天能投入多少时间？

Observation: 用户回复"没有账号，想做小红书，每天2小时"

Thought: 好的，用户是纯新人，小红书平台，每天2小时。这种情况下最关键的策略是：用最少的时间做最高杠杆的事。

Action: analyze | 分析小红书新人起号的关键杠杆点

Observation: 小红书新人起号的核心杠杆点是：封面图质量 > 标题吸引力 > 内容实用性 > 发布时间

Thought: 基于这些信息，我可以给出一个针对性的30天行动计划了。

Final Answer: 【针对小红书新人的30天起号计划】
每天2小时的配置：
• 30分钟：找热点和选题（利用第三方工具）
• 45分钟：制作封面图和标题
• 45分钟：撰写正文
• 每周复盘一次数据调整方向
前三周专注内容质量，第四周评估数据决定是否加大投入。"""
    return prompt


# ====================================================================
# 第二部分：CoT思维链 — 让AI学会"分步思考"
# ====================================================================
def demonstrate_cot():
    print("\n" + "=" * 70)
    print("🔗 第二部分：CoT思维链 — 让AI学会“分步思考”")
    print("=" * 70)

    print("""
  📖 CoT（Chain of Thought）核心原理：
    不直接输出答案 → 强制模型先输出推理过程 → 基于过程推导结果
  
  一句话总结：从"直接给答案"变成"先写解题过程，再写答案"
  """)

    # ——— 普通Prompt vs CoT Prompt 对比 ———
    print("─" * 50)
    print("📊 对比实验：普通Prompt vs CoT思维链Prompt")
    print("─" * 50)

    naive_prompt_text = """
帮我分析这个问题：自媒体新人如何快速起号，直接给出答案。
"""
    cot_prompt_text = """
你是一个专业的自媒体运营分析师。
请你一步步思考、分步推导，再给出最终完整方案：
1. 先分析新人起号的核心难点
2. 再拆解起号的关键核心要素
3. 然后给出分阶段执行步骤
4. 最后总结避坑要点和落地建议

问题：自媒体新人如何快速起号？
"""

    print("\n  📝 普通Prompt（无思维链）：")
    print(f"    {naive_prompt_text.strip()}")
    result_naive = simulate_llm(naive_prompt_text, mode="naive")
    print(f"  → 输出：{result_naive}")
    print("  ⚠️ 问题：答案笼统、逻辑单薄、步骤缺失、可落地性差")

    print("\n  📝 CoT Prompt（带分步推理）：")
    print(f"    {cot_prompt_text.strip()}")
    result_cot = simulate_llm(cot_prompt_text, mode="cot")
    print(f"  → 输出：\n{result_cot[:300]}...")
    print("\n  ✅ 效果：逻辑分层清晰、步骤完整、落地性强、无跳跃性错误")

    # ——— CoT的多种变体 ———
    print("\n" + "─" * 50)
    print("🔧 CoT的三种实用变体")
    print("─" * 50)

    variants = [
        {
            "name": "Zero-shot CoT（零样本思维链）",
            "prompt": "请一步步思考，最后给出答案。",
            "use_case": "通用场景，不需要提供示例",
            "example_prompt": "请一步步思考，分析一下当前新能源车市场的竞争格局。"
        },
        {
            "name": "Few-shot CoT（少样本思维链）",
            "prompt": "以下是一个示例：\n问题：X\n思考过程：1...2...3...\n答案：Y\n\n请按照同样的方式回答问题。",
            "use_case": "需要模型按照特定格式或风格输出",
            "example_prompt": "示例：\n问题：估算北京一年的咖啡销量\n过程：1.北京人口2200万 2.假设20%喝咖啡...\n答案：约XX亿杯\n\n请用同样的方式估算：上海一年的奶茶销量"
        },
        {
            "name": "Structured CoT（结构化思维链）",
            "prompt": "请按照以下结构输出：\n【问题分析】\n【分步推导】\n【中间结论】\n【最终答案】",
            "use_case": "需要标准化输出的商业场景",
            "example_prompt": "请按结构输出：\n【问题分析】\n【分步推导】\n【中间结论】\n【最终答案】\n\n问题：一家奶茶店月租金2万，每杯成本8元，售价18元，月固定人工4万，每月至少卖多少杯才能盈利？"
        }
    ]

    for v in variants:
        print(f"\n  🔷 {v['name']}")
        print(f"     核心Prompt：{v['prompt']}")
        print(f"     适用场景：{v['use_case']}")
        print(f"     示例：{v['example_prompt']}")


# ====================================================================
# 第三部分：ToT思维树 — 让AI学会"多路径试错"
# ====================================================================
class ToTPlanner:
    """ToT（Tree of Thought）思维树 — 多路径并行推演、择优选择"""

    def __init__(self):
        self.explored_paths = []
        self.pruned_paths = []

    def generate_paths(self, problem, num_paths=4):
        """第一步：发散多条思考路径"""
        print("\n  🌱 第1步：发散思考路径")
        print(f"     问题：{problem}")
        print(f"     生成{num_paths}条候选路径...")

        paths = [
            {
                "id": "A",
                "name": "低成本内容矩阵",
                "feasibility": 0.85,
                "cost": "低",
                "risk": "竞争激烈，出爆款概率5%-10%",
                "timeline": "30-60天见效果",
                "detail": "制作图文/短视频，利用平台自然流量，不投钱纯靠内容吸引粉丝",
                "prerequisites": ["内容创作能力", "每天2-3小时投入", "持续30天以上"],
            },
            {
                "id": "B",
                "name": "投流付费推广",
                "feasibility": 0.60,
                "cost": "高（初期5000-10000元）",
                "risk": "ROI不确定，停止投放后流量断崖式下降",
                "timeline": "3-7天见效果",
                "detail": "使用平台的付费推广工具（如DOU+、信息流广告），花钱买流量",
                "prerequisites": ["至少5000元预算", "懂投放ROI计算", "持续测试优化"],
            },
            {
                "id": "C",
                "name": "矩阵号运营",
                "feasibility": 0.75,
                "cost": "中（多账号维护成本）",
                "risk": "平台对矩阵号有限流风险，需要多个手机号注册",
                "timeline": "15-30天见效果",
                "detail": "3-5个账号同步运营，不同定位互相导流，降低单账号风险",
                "prerequisites": ["多账号管理能力", "差异化内容规划", "防关联技巧"],
            },
            {
                "id": "D",
                "name": "借势热点引流",
                "feasibility": 0.70,
                "cost": "低",
                "risk": "热点时效性短（通常1-3天），需要快速响应能力",
                "timeline": "即时见效但短暂",
                "detail": "紧跟热点话题创作，利用搜索流量和推荐算法快速获取曝光",
                "prerequisites": ["热点敏感度", "快速创作能力", "蹭热点不踩雷的判断力"],
            }
        ]
        return paths[:num_paths]

    def evaluate_paths(self, paths, constraints):
        """第二步：并行评估每条路径"""
        print("\n  📊 第2步：并行评估各路径")
        print(f"     约束条件：{constraints}")

        for p in paths:
            # 根据约束条件调整可行性评分
            score_penalty = 0
            if "预算有限" in constraints and p["cost"] == "高":
                score_penalty = 0.3
            if "每天2小时" in constraints and p["timeline"].startswith("3-7天"):
                # 短期见效的方案需要更多时间投入
                pass

            adjusted_feasibility = max(0, p["feasibility"] - score_penalty)
            p["adjusted_feasibility"] = round(adjusted_feasibility, 2)

            print(f"\n     🔷 路径{p['id']}：{p['name']}")
            print(f"        原始可行性：{p['feasibility']}  → 调整后：{p['adjusted_feasibility']}")
            print(f"        成本：{p['cost']}  |  风险：{p['risk']}")
            if score_penalty > 0:
                print(f"        ⚠️ 因'{constraints}'扣分{score_penalty}")

    def prune_and_select(self, paths, top_n=2):
        """第三步：剪枝 + 择优"""
        print(f"\n  ✂️ 第3步：剪枝择优（保留top{top_n}）")

        # 按调整后的可行性排序
        sorted_paths = sorted(paths, key=lambda p: p.get("adjusted_feasibility", p["feasibility"]), reverse=True)

        selected = sorted_paths[:top_n]
        pruned = sorted_paths[top_n:]

        self.explored_paths.extend(selected)
        self.pruned_paths.extend(pruned)

        print(f"\n     保留路径：")
        for p in selected:
            print(f"     ✅ 路径{p['id']}：{p['name']}（可行性{p.get('adjusted_feasibility', p['feasibility'])}）")

        print(f"\n     淘汰路径：")
        for p in pruned:
            print(f"     ❌ 路径{p['id']}：{p['name']}（可行性{p.get('adjusted_feasibility', p['feasibility'])}）")

        return selected

    def compose_final_plan(self, selected):
        """第四步：基于优选路径合成最终方案"""
        print("\n  🎯 第4步：合成最终方案")
        final = f"推荐策略："
        for p in selected:
            final += f"\n    • 核心路径：{p['name']}"
            final += f"\n    • 具体做法：{p['detail']}"
            final += f"\n    • 前提条件：{', '.join(p['prerequisites'])}"
            final += f"\n    • 预期见效：{p['timeline']}"
        final += "\n\n  组合策略说明：先用低成本路径A启动，同时监控路径D的热点机会\n"
        final += "  前30天以A为主，D为辅跑通内容模型，后续根据数据再决定是否引入B或C"
        return final

    def run(self, problem, constraints):
        print("\n" + "=" * 70)
        print("🌳 ToT思维树 — 多路径并行推演、择优输出")
        print("=" * 70)
        print("""
  核心逻辑：不再是单条线性思考，而是像树一样发散出多条思考路径
  
  CoT = 一条路走到黑
  ToT = 多条路同时走，选最优解
  """)
        print(f"🎯 问题：{problem}")
        print(f"📋 约束：{constraints}")

        paths = self.generate_paths(problem, 4)
        self.evaluate_paths(paths, constraints)
        selected = self.prune_and_select(paths, 2)
        final_plan = self.compose_final_plan(selected)

        print(f"\n  📋 最终方案：\n{final_plan}")
        return final_plan


# ====================================================================
# 第四部分：ReAct循环 — 让AI学会"思考+行动循环"
# ====================================================================
class ReActAgent:
    """
    ReAct（Reason + Act）交互推理循环
    工业级Agent最主流的范式，LangChain默认核心逻辑
    彻底解决"空想误判"问题
    """

    def __init__(self, task):
        self.task = task
        self.history = []
        self.max_steps = 6
        self.tool_results = {}
        self.current_step = 0

    def _simulate_tool_call(self, tool_name, params):
        """模拟调用外部工具"""
        print(f"\n      🔧 调用工具：{tool_name}")
        print(f"         参数：{params}")

        if tool_name == "web_search":
            results = {
                "2024年AI Agent市场规模": "预计2024年全球AI Agent市场规模达到240亿美元，同比增长42%。主要驱动力是企业自动化和客服场景。",
                "AI Agent落地案例": "微软Copilot、Salesforce Einstein、字节跳动Coze等。金融行业应用占比最高。",
                "AI Agent主流框架": "LangChain、CrewAI、AutoGen、Semantic Kernel。LangChain市场份额最大（约35%）。",
            }
            result = results.get(params["query"], f"关于'{params['query']}'的搜索结果：共找到12条相关结果")
            self.tool_results[tool_name] = result
            return result

        elif tool_name == "analyze_data":
            result = f"数据分析完成：{params['metric']}在过去12个月增长35%，Q2达到峰值，Q3略有回落。"
            self.tool_results[tool_name] = result
            return result

        elif tool_name == "ask_user":
            result = f"[用户回复] {params['question']} → 用户回答：是的"
            self.tool_results[tool_name] = result
            return result

        elif tool_name == "summarize":
            result = f"已汇总{params['source']}中的关键信息，提炼出3个核心要点"
            self.tool_results[tool_name] = result
            return result

        return f"[工具{tool_name}] 执行完成"

    def _simulate_think(self, context):
        """模拟LLM的思考过程"""
        step = self.current_step

        if step == 0:
            return {
                "thought": f"用户的任务是'{self.task}'。这是一个调研类任务，需要先了解行业背景，再收集具体数据，最后输出报告。让我先从搜索开始。",
                "action": "web_search",
                "params": {"query": "2024年AI Agent市场规模"}
            }
        elif step == 1:
            return {
                "thought": "我找到了市场规模数据，增长势头很好。接下来我需要了解具体的落地案例和主流框架，这样才能给出全面的分析。",
                "action": "web_search",
                "params": {"query": "AI Agent落地案例"}
            }
        elif step == 2:
            return {
                "thought": "有了市场规模和案例信息，我还需要了解有哪些主流的开发框架和技术选型，这对分析行业趋势很重要。",
                "action": "web_search",
                "params": {"query": "AI Agent主流框架"}
            }
        elif step == 3:
            return {
                "thought": "我已经收集了市场规模、落地案例和框架信息三大块数据。现在需要对这些数据进行整合分析，发现其中的趋势和关联。",
                "action": "analyze_data",
                "params": {"metric": "AI Agent行业季度增长率"}
            }
        elif step == 4:
            return {
                "thought": "数据分析和趋势已经明确。企业自动化和客服是最大驱动力，LangChain占主导地位。我现在可以生成最终的行业调研报告了。",
                "action": None,
                "params": None
            }
        else:
            return {
                "thought": "所有信息已经收集完毕，可以输出最终报告。",
                "action": None,
                "params": None
            }

    def run(self):
        print("\n" + "=" * 70)
        print("🔄 ReAct交互推理循环 — 思考→行动→观察→循环")
        print("=" * 70)
        print("""
  核心逻辑：思考一步 → 行动一步 → 观察反馈 → 继续思考
  这是目前工业级Agent最主流的范式
  
  四个关键动作：
  • Reason（思考）：判断当前需要做什么
  • Act（行动）：调用工具、获取信息、执行动作
  • Observe（观察）：接收真实反馈
  • Loop（循环）：继续下一步推理
  """)
        print(f"🎯 任务：{self.task}\n")

        while self.current_step < self.max_steps:
            decision = self._simulate_think(self.history)
            self.current_step += 1

            print(f"\n  ───── Step {self.current_step}/{self.max_steps} ─────")
            print(f"  💭 Thought（思考）：{decision['thought']}")

            action = decision.get("action")
            if action:
                params = decision.get("params", {})
                observation = self._simulate_tool_call(action, params)
                self.history.append({
                    "step": self.current_step,
                    "thought": decision["thought"],
                    "action": action,
                    "params": params,
                    "observation": observation
                })
                print(f"  👁️  Observation（观察）：{observation[:80]}...")
            else:
                self.history.append({
                    "step": self.current_step,
                    "thought": decision["thought"],
                    "action": None,
                    "params": None,
                    "observation": None
                })
                print(f"  ✅ 信息已充足，准备输出最终答案")
                break

        # 生成最终答案
        final_answer = self._compose_final_answer()
        print(f"\n  🏁 Final Answer（最终答案）：")
        print(f"     {final_answer}")
        return final_answer

    def _compose_final_answer(self):
        return f"""# 2024年AI Agent行业调研报告

## 一、市场规模
全球AI Agent市场规模预计2024年达到240亿美元，同比增长42%。
增长主要由企业自动化和智能客服场景驱动。

## 二、落地案例
- 微软Copilot：集成到Office全家桶，覆盖企业办公场景
- Salesforce Einstein：CRM领域的AI助手
- 字节跳动Coze：面向开发者的Agent构建平台
- 金融行业应用占比最高（约35%），其次是零售和 healthcare

## 三、技术框架
- LangChain：市场占有率约35%，生态最完善
- CrewAI：多Agent协作场景增长最快
- AutoGen：微软出品，对话型Agent场景
- Semantic Kernel：微软企业级方案

## 四、趋势总结
1. 从单Agent走向多Agent协作
2. 从云端走向端侧部署
3. 从通用走向垂直行业深耕
4. 从工具调用走向自主决策"""


# ====================================================================
# 第五部分：Reflexion反思 — 让AI学会"复盘纠错"
# ====================================================================
class ReflexionLoop:
    """
    Reflexion（自我反思）机制
    完成一轮任务后 → 回头复盘思考过程 → 找出漏洞 → 修正错误 → 迭代优化
    高阶Agent和普通Agent的核心差距：具备自我迭代能力
    """

    def __init__(self, task):
        self.task = task
        self.iteration = 0
        self.all_outputs = []
        self.max_iterations = 3

    def _execute_round(self, previous_feedback=None):
        """执行一轮任务"""
        self.iteration += 1

        if self.iteration == 1:
            # 第一轮：直接执行，可能有问题
            output = {
                "version": self.iteration,
                "content": f"""【第{self.iteration}版】{self.task}初步方案

核心功能清单：
1. 用户登录注册
2. 知识库管理
3. 智能问答
4. 数据统计

技术选型：
- 前端：React
- 后端：Python FastAPI
- 数据库：PostgreSQL
- AI：OpenAI API

工期预估：2个月
报价：3万元""",
                "issues": []
            }
        elif self.iteration == 2:
            # 第二轮：根据反馈优化
            output = {
                "version": self.iteration,
                "content": f"""【第{self.iteration}版】{self.task}优化方案

核心功能清单：
1. 用户登录注册（支持微信扫码）
2. 知识库管理（支持PDF/Word/TXT批量上传、自动分块）
3. 智能问答（支持多轮对话、上下文记忆、引用溯源）
4. 数据统计（日活、问答数、知识库使用率）
5. 管理后台（用户管理、权限控制、API密钥管理）

技术选型：
- 前端：React + Ant Design Pro
- 后端：Python FastAPI + Celery异步任务
- 数据库：PostgreSQL + Redis缓存
- 向量库：ChromaDB（本地部署）
- AI：OpenAI GPT-4（主）+ DeepSeek（备）

非功能需求：
- 响应时间 < 3秒
- 支持50+并发
- 数据每日备份

工期预估：3个月
报价：5万元
售后服务：首月免费维护，后续2000元/月""",
                "issues": ["缺少异常处理机制", "缺少安全防护说明"]
            }
        else:
            # 第三轮：精益求精
            output = {
                "version": self.iteration,
                "content": f"""【第{self.iteration}版】{self.task}精益版方案（已修复所有问题）

核心功能清单：
1. 用户登录注册（微信扫码 + 邮箱 + SSO）
2. 知识库管理（PDF/Word/TXT/MD批量上传、智能分块、自动清洗、增量更新）
3. 智能问答（多轮对话、上下文记忆、引用溯源[^1]、置信度评分）
4. 数据统计（日活/留存/问答质量/知识库健康度）
5. 管理后台（RBAC权限、租户隔离、操作审计、API密钥管理）

技术选型：
- 前端：React + Ant Design Pro + TypeScript
- 后端：Python FastAPI + Celery + WebSocket流式输出
- 数据库：PostgreSQL（主）+ Redis（缓存/队列）
- 向量库：ChromaDB（私有化部署）
- AI：OpenAI GPT-4（主）+ DeepSeek（备）+ 本地模型兜底

安全防护：
- 所有API通过Gateway统一鉴权
- 敏感数据AES-256加密存储
- 输入注入检测 + 输出脱敏
- 操作日志全链路审计
- 限流熔断（按用户/接口/租户三级）

异常处理：
- 全局异常捕获 + 友好提示
- 重试机制（指数退避，最多3次）
- 降级方案（AI不可用时用缓存兜底）
- 熔断机制（连续失败自动切断）

非功能保障：
- P99响应时间 < 3秒
- 支持200+并发
- 可用性99.5%
- 数据每日全量备份 + 增量实时备份

工期预估：3.5个月
报价：7万元
售后服务：首月免费，后续维护合同3000元/月或按次计费""",
                "issues": []
            }

        self.all_outputs.append(output)
        return output

    def _reflect(self, output):
        """反思检查当前输出的问题"""
        print(f"\n      🔍 自检维度：")
        checks = []

        # 维度1：完整性检查
        completeness_issues = []
        if "知识库管理" not in output["content"]:
            completeness_issues.append("缺少知识库管理模块")
        if "安全" not in output["content"] and "security" not in output["content"].lower():
            completeness_issues.append("缺少安全防护措施")
        if "报价" not in output["content"]:
            completeness_issues.append("缺少报价信息")
        if "工期" not in output["content"]:
            completeness_issues.append("缺少工期预估")
        if completeness_issues:
            checks.append({"维度": "完整性", "问题": completeness_issues, "严重度": "高"})

        # 维度2：细节检查
        detail_issues = []
        if "异常" not in output["content"]:
            detail_issues.append("缺少异常处理机制")
        if "备份" not in output["content"]:
            detail_issues.append("缺少数据备份方案")
        if "售后" not in output["content"] and "维护" not in output["content"]:
            detail_issues.append("缺少售后服务说明")
        if detail_issues:
            checks.append({"维度": "细节完整性", "问题": detail_issues, "严重度": "中"})

        # 维度3：专业性检查
        professional_issues = []
        if "版" in output["content"] and output["version"] > 1:
            # 已经是迭代版本，检查是否解决了之前的问题
            if output["version"] == 2 and self._has_stale_issues(output):
                professional_issues.append("上一轮的问题未完全修复")
        if professional_issues:
            checks.append({"维度": "专业性", "问题": professional_issues, "严重度": "中"})

        return checks

    def _has_stale_issues(self, output):
        """检查是否还有遗留问题"""
        return "缺少" in output["content"] and output["version"] < 3

    def run(self):
        print("\n" + "=" * 70)
        print("🪞 Reflexion自我反思 — 复盘纠错、迭代优化")
        print("=" * 70)
        print("""
  核心逻辑：完成一轮任务 → 回头复盘找出漏洞 → 修正错误 → 再次执行
  
  前面三种范式解决"怎么思考、怎么执行"
  Reflexion解决的是"怎么越做越对、越做越好"
  """)
        print(f"🎯 任务：{self.task}\n")

        for iteration in range(self.max_iterations):
            print(f"  ───── 第{iteration + 1}轮 ─────")
            print(f"  🏗️  执行生成...")
            output = self._execute_round()

            print(f"  📋 输出预览：{output['content'][:100]}...")

            print(f"\n  🔎 开始反思检查...")
            issues = self._reflect(output)

            if not issues:
                print(f"\n  ✅ 第{iteration + 1}轮输出通过所有检查！")
                print(f"\n  🏁 最终输出：\n{output['content']}")
                return output["content"]
            else:
                print(f"\n  ⚠️ 发现{sum(len(c['问题']) for c in issues)}个问题：")
                for check in issues:
                    for problem in check["问题"]:
                        print(f"     [{check['严重度']}][{check['维度']}] {problem}")

                if iteration < self.max_iterations - 1:
                    print(f"\n  🔄 准备第{iteration + 2}轮优化...")
                else:
                    print(f"\n  ⚠️ 已达最大迭代次数，输出当前最优版本")
                    print(f"\n  🏁 最终输出：\n{output['content']}")
                    return output["content"]

        return self.all_outputs[-1]["content"]


# ====================================================================
# 第六部分：四种范式对比与选型建议
# ====================================================================
def paradigm_comparison():
    print("\n" + "=" * 70)
    print("📊 第六部分：四种范式对比与选型指南")
    print("=" * 70)

    comparison = [
        {
            "范式": "CoT 思维链",
            "核心逻辑": "分步推理 → 逐步推导 → 输出结果",
            "适合场景": "简单问答、文案、推理、计算类任务",
            "不适合场景": "需要调用外部工具、需要多轮交互",
            "实现复杂度": "⭐ 极低（就是Prompt中加一句话）",
            "效率": "⭐⭐⭐⭐⭐",
            "精度": "⭐⭐⭐⭐",
            "一句话总结": "所有Agent规划能力的基础底座"
        },
        {
            "范式": "ToT 思维树",
            "核心逻辑": "发散多条路径 → 并行推演 → 择优选择",
            "适合场景": "复杂决策、方案设计、多维度分析",
            "不适合场景": "简单问答（杀鸡用牛刀）、实时对话（延迟较高）",
            "实现复杂度": "⭐⭐⭐ 中等（需要管理多条路径状态）",
            "效率": "⭐⭐⭐",
            "精度": "⭐⭐⭐⭐⭐",
            "一句话总结": "多条路同时走，选最优解"
        },
        {
            "范式": "ReAct 交互推理",
            "核心逻辑": "思考 → 行动 → 观察 → 循环",
            "适合场景": "需要工具调用、联网搜索、自动化执行",
            "不适合场景": "纯文本推理（不需要工具）、简单对话",
            "实现复杂度": "⭐⭐⭐⭐ 较高（需要工具管理+循环控制）",
            "效率": "⭐⭐⭐⭐",
            "精度": "⭐⭐⭐⭐",
            "一句话总结": "工业级Agent最主流的范式"
        },
        {
            "范式": "Reflexion 自我反思",
            "核心逻辑": "执行 → 复盘 → 纠错 → 迭代优化",
            "适合场景": "高精度要求、低幻觉要求、需要持续优化的场景",
            "不适合场景": "实时对话（延迟增加）、简单任务（过度设计）",
            "实现复杂度": "⭐⭐⭐ 中等（需要保存历史+对比逻辑）",
            "效率": "⭐⭐",
            "精度": "⭐⭐⭐⭐⭐",
            "一句话总结": "让AI越做越对、越做越好"
        }
    ]

    print(f"\n{'范式名称':<24}{'适合场景':<30}{'不适合场景':<30}{'复杂度':<16}{'一句话总结'}")
    print("─" * 120)
    for p in comparison:
        print(f"{p['范式']:<24}{p['适合场景']:<30}{p['不适合场景'][:28]:<30}{p['实现复杂度'][:14]:<16}{p['一句话总结']}")

    print("\n" + "─" * 50)
    print("🎯 新手选型标准")
    print("─" * 50)
    print("""
  简单问答、文案、推理任务              → CoT 思维链
  复杂决策、方案设计、多维度分析        → ToT 思维树
  需要工具调用、联网、落地执行          → ReAct 循环推理
  需要高精度、低幻觉、持续优化          → 叠加 Reflexion 反思机制

  💡 所有商用全自动Agent，本质都是这四种范式的组合堆叠
  💡 推荐的入门路径：先从 CoT 开始 → 再引入 ReAct → 逐步叠加 ToT 和 Reflexion
  """)

    print("─" * 50)
    print("🏗️  常见组合方案")
    print("─" * 50)
    combinations = [
        {
            "方案": "基础问答Agent",
            "组合": "CoT",
            "适用": "知识库问答、客服、内容生成"
        },
        {
            "方案": "研究分析Agent",
            "组合": "CoT + ReAct",
            "适用": "市场调研、竞品分析、数据报告",
            "说明": "用CoT保证分析质量，用ReAct调用搜索工具获取信息"
        },
        {
            "方案": "自动化执行Agent",
            "组合": "ReAct + Reflexion",
            "适用": "办公自动化、任务调度、数据处理",
            "说明": "用ReAct完成工具调用循环，用Reflexion确保执行质量"
        },
        {
            "方案": "专家级决策Agent",
            "组合": "CoT + ToT + ReAct + Reflexion",
            "适用": "复杂项目方案、战略规划、长周期任务",
            "说明": "全范式组合，最高精度"
        }
    ]
    for c in combinations:
        print(f"\n  🔷 {c['方案']}")
        print(f"     组合：{c['组合']}")
        print(f"     适用：{c['适用']}")
        if "说明" in c:
            print(f"     说明：{c['说明']}")


# ====================================================================
# 第七部分：进阶 — 全自动任务拆解模拟
# ====================================================================
class AutoTaskDecomposer:
    """
    真正的Agent规划：全自动任务拆解
    让模型自主拆解未知复杂任务，无需人工定义步骤
    
    规划模块自动完成：
    1. 目标理解与校准
    2. 复杂任务子任务拆分
    3. 执行优先级排序
    4. 判断是否需要调用工具
    5. 分步执行、循环推进
    6. 全程自我校验纠错
    """

    def __init__(self):
        self.task_graph = []
        self.current_status = {}
        self.errors = []

    def understand_goal(self, raw_goal):
        """第1步：目标理解与校准"""
        print("\n" + "─" * 50)
        print("🔍 第1步：目标理解与校准")
        print("─" * 50)

        understanding = {
            "raw_goal": raw_goal,
            "core_objective": self._extract_core(raw_goal),
            "scope": self._determine_scope(raw_goal),
            "estimated_complexity": self._estimate_complexity(raw_goal),
            "required_capabilities": self._identify_capabilities(raw_goal),
        }

        print(f"  📥 原始目标：{raw_goal}")
        print(f"  🎯 核心目标：{understanding['core_objective']}")
        print(f"  📏 范围界定：{understanding['scope']}")
        print(f"  📊 预估复杂度：{understanding['estimated_complexity']}")
        print(f"  🔧 需要能力：")

        for cap in understanding["required_capabilities"]:
            print(f"     • {cap}")

        return understanding

    def _extract_core(self, goal):
        """从模糊目标中提取核心意图"""
        goal_lower = goal.lower()

        if "调研" in goal_lower or "分析" in goal_lower:
            return "完成行业调研分析报告"
        elif "搭建" in goal_lower or "开发" in goal_lower or "创建" in goal_lower:
            return "搭建可运行的AI系统"
        elif "计划" in goal_lower or "规划" in goal_lower:
            return "制定可执行的行动计划"
        elif "写" in goal_lower or "生成" in goal_lower or "创作" in goal_lower:
            return "创作高质量内容"
        else:
            return "理解并完成用户提出的综合任务"

    def _determine_scope(self, goal):
        """确定任务范围"""
        goal_lower = goal.lower()
        if "竞品" in goal_lower or "市场" in goal_lower:
            return "需要全网信息搜索，涉及多个维度的对比分析"
        elif "开发" in goal_lower or "搭建" in goal_lower:
            return "需要技术方案设计、技术选型、架构规划"
        elif "内容" in goal_lower or "文章" in goal_lower:
            return "需要选题策划、内容结构设计、素材收集"
        return "综合性任务，覆盖多个维度"

    def _estimate_complexity(self, goal):
        """估算复杂度"""
        goal_lower = goal.lower()
        score = 0
        score += 1 if "调研" in goal_lower else 0
        score += 1 if "竞品" in goal_lower else 0
        score += 1 if "报告" in goal_lower else 0
        score += 1 if "对比" in goal_lower else 0
        score += 1 if "搭建" in goal_lower or "开发" in goal_lower else 0
        score += 1 if "多" in goal_lower or "综合" in goal_lower else 0

        if score <= 1:
            return "⭐ 简单（1-2个子任务）"
        elif score <= 3:
            return "⭐⭐ 中等（3-5个子任务）"
        else:
            return "⭐⭐⭐ 复杂（5+个子任务，需多轮迭代）"

    def _identify_capabilities(self, goal):
        """识别需要的能力"""
        capabilities = ["语言理解与生成"]
        goal_lower = goal.lower()

        if "搜索" in goal_lower or "调研" in goal_lower or "竞品" in goal_lower:
            capabilities.append("联网搜索与信息检索")
        if "对比" in goal_lower or "分析" in goal_lower:
            capabilities.append("数据分析与对比")
        if "报告" in goal_lower or "输出" in goal_lower:
            capabilities.append("结构化文档生成")
        if "代码" in goal_lower or "开发" in goal_lower or "搭建" in goal_lower:
            capabilities.append("代码生成与技术实现")

        return capabilities

    def decompose_tasks(self, understanding):
        """第2步：复杂任务拆解为子任务"""
        print("\n" + "─" * 50)
        print("📋 第2步：复杂任务拆解为可执行子任务")
        print("─" * 50)

        subtasks = [
            {
                "id": "T1",
                "name": "信息收集与整理",
                "description": "收集行业基础数据、市场报告、竞品信息",
                "estimated_hours": 4,
                "dependencies": [],
                "needs_tool": True,
                "tool": "web_search",
            },
            {
                "id": "T2",
                "name": "数据清洗与结构化",
                "description": "将收集到的零散信息进行分类、去重、结构化存储",
                "estimated_hours": 2,
                "dependencies": ["T1"],
                "needs_tool": False,
                "tool": None,
            },
            {
                "id": "T3",
                "name": "多维度对比分析",
                "description": "从市场规模、技术路线、商业模式等维度进行横向对比",
                "estimated_hours": 3,
                "dependencies": ["T2"],
                "needs_tool": True,
                "tool": "analyze_data",
            },
            {
                "id": "T4",
                "name": "核心结论提炼",
                "description": "基于分析结果，提炼关键发现和趋势判断",
                "estimated_hours": 1,
                "dependencies": ["T3"],
                "needs_tool": False,
                "tool": None,
            },
            {
                "id": "T5",
                "name": "报告撰写与格式编排",
                "description": "将分析结果整理为结构化报告，包含摘要、正文、建议",
                "estimated_hours": 3,
                "dependencies": ["T4"],
                "needs_tool": False,
                "tool": None,
            },
            {
                "id": "T6",
                "name": "质量检查与修正",
                "description": "检查报告完整性、准确性、逻辑一致性，修正问题",
                "estimated_hours": 1,
                "dependencies": ["T5"],
                "needs_tool": False,
                "tool": None,
            },
        ]

        print(f"  总共拆分为{len(subtasks)}个子任务：")
        for task in subtasks:
            dep_str = f"依赖：{', '.join(task['dependencies'])}" if task["dependencies"] else "无依赖"
            tool_str = f"需要工具：{task['tool']}" if task["needs_tool"] else "无需工具"
            print(f"\n     🔷 {task['id']}：{task['name']}")
            print(f"        {task['description']}")
            print(f"        预估工时：{task['estimated_hours']}h | {dep_str} | {tool_str}")

        return subtasks

    def priority_sort(self, subtasks):
        """第3步：执行优先级排序"""
        print("\n" + "─" * 50)
        print("📊 第3步：执行优先级排序")
        print("─" * 50)

        # 拓扑排序（处理依赖关系）
        sorted_tasks = []
        remaining = list(subtasks)
        max_iterations = len(remaining) * 2
        iteration = 0

        while remaining and iteration < max_iterations:
            iteration += 1
            ready = []
            for task in remaining:
                deps = task["dependencies"]
                if all(d in [t["id"] for t in sorted_tasks] for d in deps):
                    ready.append(task)

            if not ready:
                print("  ⚠️ 检测到依赖循环，强制跳出")
                break

            # 按依赖数量排序（依赖少的优先）
            ready.sort(key=lambda t: len(t["dependencies"]))
            for task in ready:
                sorted_tasks.append(task)
                remaining.remove(task)

        # 如果有剩余任务，追加
        sorted_tasks.extend(remaining)

        print(f"  执行顺序：")
        for i, task in enumerate(sorted_tasks, 1):
            print(f"    Step {i}: {task['id']} {task['name']} ({task['estimated_hours']}h)")

        total_hours = sum(t["estimated_hours"] for t in sorted_tasks)
        print(f"\n  ⏱️  预估总工时：{total_hours}h")
        return sorted_tasks

    def run(self, raw_goal):
        """完整执行全自动任务拆解流程"""
        print("\n" + "=" * 70)
        print("🏗️  第七部分：进阶 — 全自动任务拆解")
        print("=" * 70)
        print("""
  真正的Agent规划 vs 基础CoT：
  
  CoT是基础思维优化 → 需要人工在Prompt中定义步骤
  全自动任务拆解 → 模型自主完成所有规划逻辑，无需人工干预
  """)
        print(f"🎯 输入模糊目标：{raw_goal}")

        understanding = self.understand_goal(raw_goal)
        subtasks = self.decompose_tasks(understanding)
        sorted_tasks = self.priority_sort(subtasks)

        print("\n" + "─" * 50)
        print("✅ 任务规划完成！总结：")
        print("─" * 50)
        print(f"  目标：{understanding['core_objective']}")
        print(f"  拆解：{len(sorted_tasks)}个子任务，按依赖关系排序")
        print(f"  需工具调用：{sum(1 for t in sorted_tasks if t['needs_tool'])}个子任务")
        print(f"  总工时：{sum(t['estimated_hours'] for t in sorted_tasks)}h")
        print(f"  接下来：按排序顺序依次执行，每步完成后检查，发现异常立即纠正")

        return {
            "understanding": understanding,
            "task_graph": sorted_tasks
        }


# ====================================================================
# Main：展示所有功能
# ====================================================================
if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "🧠 第3篇：思维链与规划能力" + " " * 21 + "║")
    print("║" + " " * 12 + "AI Agent从入门到实战 — 完整代码实现" + " " * 12 + "║")
    print("╚" + "═" * 68 + "╝")

    # 第一部分：三大缺陷
    demonstrate_llm_defects()

    input("\n\n按 Enter 继续演示 CoT 思维链...")

    # 第二部分：CoT
    demonstrate_cot()

    input("\n\n按 Enter 继续演示 ToT 思维树...")

    # 第三部分：ToT
    tot = ToTPlanner()
    tot.run(
        problem="自媒体新人如何快速起号",
        constraints="预算有限，每天能投入2小时"
    )

    input("\n\n按 Enter 继续演示 ReAct 循环...")

    # 第四部分：ReAct
    react = ReActAgent("调研2024年AI Agent行业趋势")
    react.run()

    input("\n\n按 Enter 继续演示 Reflexion 反思...")

    # 第五部分：Reflexion
    reflexion = ReflexionLoop("给我出一份完整的AI知识库问答系统方案")
    reflexion.run()

    input("\n\n按 Enter 继续查看范式对比...")

    # 第六部分：对比
    paradigm_comparison()

    input("\n\n按 Enter 继续演示全自动任务拆解...")

    # 第七部分：全自动任务拆解
    decomposer = AutoTaskDecomposer()
    decomposer.run("帮我做一个AI Agent行业的竞品调研，对比主要玩家和产品差异，输出一份完整的分析报告")

    print("\n\n" + "═" * 70)
    print("✅ 全部演示完成！")
    print("═" * 70)
    print("""
  本篇完整覆盖了以下核心内容：
  
  🧩 第一部分：大模型"单次输出"的三大天生缺陷
      → 任务一锅烩、无中间推理、无法迭代推进
  
  🔗 第二部分：CoT思维链 — 分步推理的威力
      → 普通Prompt vs CoT Prompt 效果对比
      → Zero-shot / Few-shot / Structured 三种变体
  
  🌳 第三部分：ToT思维树 — 多路径择优
      → 发散→评估→剪枝→合成 四步流程
  
  🔄 第四部分：ReAct循环 — 思考+行动
      → Thought→Action→Observation→Loop 完整循环
      → 多工具调用、多步协作
  
  🪞 第五部分：Reflexion反思 — 复盘纠错
      → 三轮迭代优化，每轮找出问题并修复
  
  📊 第六部分：四种范式对比与选型
      → 完整对比表 + 新手选型标准 + 组合方案
  
  🏗️  第七部分：进阶 — 全自动任务拆解
      → 目标理解→子任务拆分→优先级排序→工具判断
  """)
