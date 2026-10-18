# 第7篇配套代码：AI Agent开发框架选型对比
# 五大主流框架对比与场景匹配
# 运行：python 01_framework_comparison.py

# ========== 框架对照表 ==========
frameworks = {
    "LangChain": {
        "定位": "通用Agent开发框架",
        "核心能力": "链式编排、工具调用、RAG集成、记忆管理",
        "适合场景": "企业级Agent、复杂工作流、RAG系统",
        "学习成本": "⭐⭐⭐⭐（较高）",
        "推荐指数": "⭐⭐⭐⭐",
        "一句话": "功能最全，但学习曲线陡峭"
    },
    "LlamaIndex": {
        "定位": "数据索引与RAG框架",
        "核心能力": "文档索引、向量检索、知识库问答",
        "适合场景": "知识库系统、文档问答、数据分析",
        "学习成本": "⭐⭐⭐（中等）",
        "推荐指数": "⭐⭐⭐⭐⭐",
        "一句话": "RAG场景首选，数据连接能力极强"
    },
    "CrewAI": {
        "定位": "多智能体协作框架",
        "核心能力": "角色分配、任务委派、Agent协作",
        "适合场景": "多Agent分工、自动化团队",
        "学习成本": "⭐⭐（较低）",
        "推荐指数": "⭐⭐⭐⭐",
        "一句话": "多Agent协作最简单方案"
    },
    "AutoGen": {
        "定位": "多Agent对话框架",
        "核心能力": "多Agent对话、代码生成、群聊模式",
        "适合场景": "复杂推理、多轮对话协作",
        "学习成本": "⭐⭐⭐（中等）",
        "推荐指数": "⭐⭐⭐",
        "一句话": "微软出品，多Agent对话能力强"
    },
    "AutoGPT": {
        "定位": "自主任务执行框架",
        "核心能力": "自主规划、长周期任务、互联网访问",
        "适合场景": "全自动长周期任务",
        "学习成本": "⭐⭐（较低）",
        "推荐指数": "⭐⭐",
        "一句话": "概念领先但生产可用性待提升"
    }
}

# ========== 场景匹配推荐 ==========
def recommend_framework(scene):
    """根据场景推荐框架"""
    scene_map = {
        "知识库问答": "LlamaIndex",
        "多工具办公自动化": "LangChain",
        "多智能体团队协作": "CrewAI",
        "复杂推理对话": "AutoGen",
        "自主长周期任务": "AutoGPT",
        "新手入门": "LangChain + CrewAI",
        "商业项目": "LangChain + LlamaIndex",
        "个人副业": "CrewAI / LlamaIndex"
    }
    return scene_map.get(scene, "LangChain（通用）")

# ========== 新手推荐技术栈 ==========
def beginner_stack():
    return """
📚 新手最优技术栈（2026版）：

1️⃣ 入门期（1-4周）：
   - 手写基础Agent（第8篇）→ 理解原理
   - 搭配极简RAG（第9篇）

2️⃣ 进阶期（5-8周）：
   - CrewAI → 快速搭建多Agent
   - 或 LangChain → 复杂工作流

3️⃣ 商业期（9周+）：
   - LangChain + LlamaIndex 组合
   - FastAPI 部署
   - 私有化知识库封装
"""

if __name__ == "__main__":
    print("=" * 60)
    print("AI Agent 开发框架选型对比")
    print("=" * 60)
    
    for name, info in frameworks.items():
        print(f"\n{'─' * 50}")
        print(f"🔷 {name}")
        print(f"  定位：{info['定位']}")
        print(f"  核心能力：{info['核心能力']}")
        print(f"  适合场景：{info['适合场景']}")
        print(f"  学习成本：{info['学习成本']}")
        print(f"  推荐指数：{info['推荐指数']}")
        print(f"  一句话：{info['一句话']}")
    
    print("\n" + "=" * 60)
    print("场景推荐")
    print("=" * 60)
    scenes = ["知识库问答", "多工具办公自动化", "多智能体团队协作", "新手入门", "商业项目"]
    for scene in scenes:
        rec = recommend_framework(scene)
        print(f"  {scene} → 推荐：{rec}")
    
    print(beginner_stack())
