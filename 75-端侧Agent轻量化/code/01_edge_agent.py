# 第75篇配套代码：端侧Agent轻量化
# 小模型选型、量化压缩、端云协同落地
# 运行：python 01_edge_agent.py

import json

# ========== 小模型选型对比 ==========
class SmallModelSelector:
    """端侧小模型选型"""
    
    MODELS = {
        "Qwen2-0.5B": {
            "参数": "0.5B",
            "内存需求": "~1GB",
            "量化后大小": "~300MB",
            "速度(tokens/s)": "30-50",
            "精度": "中等",
            "适合场景": "简单问答、文本分类"
        },
        "Qwen2-1.5B": {
            "参数": "1.5B",
            "内存需求": "~3GB",
            "量化后大小": "~800MB",
            "速度(tokens/s)": "20-35",
            "精度": "良好",
            "适合场景": "通用问答、内容生成"
        },
        "Phi-3-mini": {
            "参数": "3.8B",
            "内存需求": "~8GB",
            "量化后大小": "~2GB",
            "速度(tokens/s)": "15-25",
            "精度": "优秀",
            "适合场景": "复杂推理、代码生成"
        },
        "Gemma-2B": {
            "参数": "2B",
            "内存需求": "~4GB",
            "量化后大小": "~1.2GB",
            "速度(tokens/s)": "25-40",
            "精度": "良好",
            "适合场景": "对话、文本处理"
        }
    }
    
    @staticmethod
    def recommend(hardware, task_type):
        """根据硬件和任务推荐"""
        if hardware == "mobile":
            if task_type in ["simple_qa", "classification"]:
                return "Qwen2-0.5B"
            else:
                return "Qwen2-1.5B"
        elif hardware == "edge":
            if task_type in ["reasoning", "code"]:
                return "Phi-3-mini"
            else:
                return "Gemma-2B"
        else:  # server
            return "Phi-3-mini"

# ========== 量化策略 ==========
class QuantizationStrategy:
    """模型量化策略"""
    
    @staticmethod
    def get_strategies():
        return {
            "INT8量化": {
                "压缩率": "50%",
                "精度损失": "~1-2%",
                "速度提升": "2x",
                "兼容性": "大多数模型",
                "推荐场景": "通用端侧部署"
            },
            "INT4量化": {
                "压缩率": "75%",
                "精度损失": "~3-5%",
                "速度提升": "3x",
                "兼容性": "部分模型",
                "推荐场景": "内存受限场景"
            },
            "FP16量化": {
                "压缩率": "50%",
                "精度损失": "~0.1%",
                "速度提升": "1.5x",
                "兼容性": "大多数模型",
                "推荐场景": "精度优先场景"
            },
            "GGUF(GGML)": {
                "压缩率": "60-80%",
                "精度损失": "~2-4%",
                "速度提升": "2-4x",
                "兼容性": "LLaMA系列",
                "推荐场景": "CPU推理"
            }
        }

# ========== 端云协同 ==========
class EdgeCloudCoordination:
    """端云协同策略"""
    
    @staticmethod
    def get_strategy():
        return """
# 端云协同策略

┌─────────────┐          ┌──────────────┐
│  端侧(Edge) │          │  云端(Cloud) │
├─────────────┤          ├──────────────┤
│ • 简单推理  │ ←→ 协同 →│ • 复杂推理   │
│ • 本地缓存  │          │ • 知识库检索  │
│ • 离线可用  │          │ • 大模型调用  │
│ • 快速响应  │          │ • 模型更新   │
└─────────────┘          └──────────────┘

## 分流规则
1. 简单问题（5秒内可答）→ 端侧处理
2. 复杂问题 → 云端处理
3. 离线 → 端侧兜底
4. 高频场景 → 端侧缓存
5. 知识库查询 → 云端检索
"""
    
    @staticmethod
    def route_request(question, edge_capable):
        """请求路由"""
        simple_keywords = ["你好", "天气", "时间", "日期", "计算", "翻译"]
        
        is_simple = any(kw in question for kw in simple_keywords)
        question_short = len(question) < 20
        
        if is_simple and question_short and edge_capable:
            return {"route": "edge", "reason": "简单问题，端侧处理"}
        else:
            return {"route": "cloud", "reason": "复杂问题，云端处理"}

# ========== 性能评估 ==========
class EdgeBenchmark:
    """端侧性能评估"""
    
    @staticmethod
    def estimate_performance(model_size_b, quantized=True):
        """估算端侧性能"""
        if quantized:
            memory = model_size_b * 0.5  # 量化后减少50%
            speed = 50 - model_size_b * 10  # 速度估算
        else:
            memory = model_size_b * 2
            speed = 30 - model_size_b * 5
        
        return {
            "模型大小(B)": model_size_b,
            "是否量化": quantized,
            "内存需求(GB)": round(memory, 1),
            "推理速度(tokens/s)": max(int(speed), 5),
            "适合场景": "端侧" if memory < 4 else "边缘端" if memory < 8 else "服务器"
        }

if __name__ == "__main__":
    print("=" * 60)
    print("📱 端侧Agent轻量化")
    print("=" * 60)
    
    # 1. 小模型选型
    print("\n1️⃣ 小模型选型对比")
    print("-" * 40)
    for name, info in SmallModelSelector.MODELS.items():
        print(f"\n  🔷 {name}")
        for k, v in info.items():
            print(f"    {k}：{v}")
    
    print("\n推荐测试：")
    for hw, task in [("mobile", "simple_qa"), ("mobile", "reasoning"), ("edge", "reasoning")]:
        rec = SmallModelSelector.recommend(hw, task)
        print(f"  {hw} + {task} → {rec}")
    
    # 2. 量化策略
    print("\n2️⃣ 量化策略")
    print("-" * 40)
    for name, info in QuantizationStrategy.get_strategies().items():
        print(f"\n  🔷 {name}")
        for k, v in info.items():
            print(f"    {k}：{v}")
    
    # 3. 端云协同
    print("\n3️⃣ 端云协同")
    print("-" * 40)
    print(EdgeCloudCoordination.get_strategy())
    
    # 测试路由
    coordinator = EdgeCloudCoordination()
    questions = [
        ("你好，你是谁？", True),
        ("帮我分析一下2024年AI行业趋势，包括市场规模、主要玩家、技术创新方向", True),
        ("现在几点了？", True),
        ("根据这三份文档生成一份详细的分析报告", False)
    ]
    for q, capable in questions:
        result = coordinator.route_request(q, capable)
        print(f"  {q[:30]}... → {result['route']}（{result['reason']}）")
    
    # 4. 性能评估
    print("\n4️⃣ 性能评估")
    print("-" * 40)
    for size in [0.5, 1.5, 3.8, 7]:
        perf = EdgeBenchmark.estimate_performance(size, quantized=True)
        print(f"  {size}B模型→内存{perf['内存需求(GB)']}GB→速度{perf['推理速度(tokens/s)']}t/s→{perf['适合场景']}")
