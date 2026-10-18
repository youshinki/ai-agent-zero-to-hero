# 第52篇配套代码：Agent核心架构总览
# 从LLM到自主决策完整链路
# 运行：python 01_agent_architecture.py

# ========== Agent核心架构 ==========
class AgentArchitecture:
    """从LLM到自主决策的完整链路"""
    
    def __init__(self):
        self.components = {
            "LLM层": {
                "description": "大语言模型核心推理引擎",
                "models": ["GPT-4", "Claude", "DeepSeek", "Qwen"],
                "responsibility": "理解、推理、生成、决策"
            },
            "感知层": {
                "description": "接收和理解外部输入",
                "sub_components": ["输入解析", "意图识别", "实体提取", "上下文理解"],
                "responsibility": "将用户输入转为结构化指令"
            },
            "规划层": {
                "description": "任务拆解和执行规划",
                "sub_components": ["目标分解", "步骤编排", "优先级排序", "依赖管理"],
                "responsibility": "将复杂任务拆为可执行子任务"
            },
            "记忆层": {
                "description": "信息存储和检索",
                "sub_components": ["短期记忆", "长期记忆", "向量存储", "记忆压缩"],
                "responsibility": "跨会话保持知识和上下文"
            },
            "工具层": {
                "description": "外部能力和API集成",
                "sub_components": ["函数调用", "API集成", "代码执行", "文件操作"],
                "responsibility": "扩展Agent的行动能力"
            },
            "反思层": {
                "description": "自我检查和纠错",
                "sub_components": ["结果验证", "错误检测", "迭代优化", "经验沉淀"],
                "responsibility": "保证输出质量和准确性"
            },
            "执行层": {
                "description": "最终输出和行动",
                "sub_components": ["结果生成", "动作执行", "反馈收集"],
                "responsibility": "将决策转化为实际行动"
            }
        }
    
    def show_architecture(self):
        print("=" * 60)
        print("🤖 AI Agent 核心架构总览")
        print("从LLM到自主决策的完整链路")
        print("=" * 60)
        
        layers = list(self.components.keys())
        for i, (name, info) in enumerate(self.components.items()):
            prefix = "┌─" if i == 0 else "│  " if i < len(layers) - 1 else "└─"
            print(f"\n{prefix} {name}")
            print(f"│  ├─ 职责：{info['responsibility']}")
            print(f"│  ├─ 说明：{info['description']}")
            if "sub_components" in info:
                print(f"│  └─ 子组件：{', '.join(info['sub_components'])}")
            print(f"│  └─ 实例：{', '.join(info.get('models', ['N/A']))}")
            if i < len(layers) - 1:
                print("│  ↓")

# ========== 数据流展示 ==========
class DataFlow:
    """数据在Agent各层之间的流转"""
    
    @staticmethod
    def show_flow(user_input):
        print(f"\n📥 输入：{user_input}")
        print("\n数据流转路径：")
        steps = [
            ("感知层", "解析用户输入，识别意图为'生成周报'"),
            ("规划层", "拆解任务：收集数据→分析→生成报告→检查"),
            ("记忆层", "检索用户历史偏好（格式/风格）"),
            ("工具层", "调用数据读取工具获取本周数据"),
            ("LLM层", "LLM整合信息生成周报内容"),
            ("反思层", "检查完整性和准确性"),
            ("执行层", "输出最终周报")
        ]
        for i, (layer, action) in enumerate(steps, 1):
            print(f"  {i}. [{layer}] {action}")

# ========== Agent类型 ==========
class AgentTypes:
    """Agent类型分类"""
    
    @staticmethod
    def get_types():
        return {
            "ReAct Agent": {
                "pattern": "思考→行动→观察→再思考",
                "use_case": "工具调用、信息搜索",
                "complexity": "中等"
            },
            "Plan-and-Execute": {
                "pattern": "先规划全部步骤→逐一执行",
                "use_case": "长周期复杂任务",
                "complexity": "高"
            },
            "Reflexion Agent": {
                "pattern": "执行→反思→改进→再执行",
                "use_case": "需要高质量输出的场景",
                "complexity": "高"
            },
            "Multi-Agent": {
                "pattern": "多个Agent分工协作",
                "use_case": "复杂系统、团队协作",
                "complexity": "很高"
            }
        }

if __name__ == "__main__":
    arch = AgentArchitecture()
    arch.show_architecture()
    
    print("\n\n" + "=" * 60)
    print("📊 数据流演示")
    print("=" * 60)
    DataFlow.show_flow("帮我生成本周工作周报")
    
    print("\n\n" + "=" * 60)
    print("📋 Agent类型对比")
    print("=" * 60)
    for name, info in AgentTypes.get_types().items():
        print(f"\n  🔷 {name}")
        print(f"    模式：{info['pattern']}")
        print(f"    场景：{info['use_case']}")
        print(f"    复杂度：{info['complexity']}")
