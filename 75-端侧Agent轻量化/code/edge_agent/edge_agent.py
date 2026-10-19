#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第75篇配套完整项目代码 · edge_agent.py
端侧Agent轻量化：小模型选型、量化压缩、端云协同落地

  1. 设备能力检测与模型选型
  2. 量化压缩估算（INT8/INT4/FP16）
  3. 端云协同路由（简单本地/复杂云端）
  4. 离线降级
  5. 性能与成本对比
==========================================================================
"""

from typing import Dict, List


# ======================================================================
# 一、模型库
# ======================================================================

MODELS = {
    "qwen2-0.5b": {"params_b": 0.5, "quality": 5, "speed": 45,
                   "ram_gb": 1.0},
    "qwen2-1.5b": {"params_b": 1.5, "quality": 7, "speed": 30,
                   "ram_gb": 3.0},
    "phi3-mini": {"params_b": 3.8, "quality": 9, "speed": 20,
                  "ram_gb": 8.0},
    "gemma-2b": {"params_b": 2.0, "quality": 7.5, "speed": 25,
                 "ram_gb": 4.0},
}

QUANTIZATION = {
    "FP16": {"ratio": 1.0, "loss": 0.0, "note": "原始精度"},
    "INT8": {"ratio": 0.5, "loss": 0.02, "note": "压缩50%，损失~2%"},
    "INT4": {"ratio": 0.3, "loss": 0.05, "note": "压缩70%，损失~5%"},
}


# ======================================================================
# 二、设备与选型
# ======================================================================

class Device:
    def __init__(self, name: str, ram_gb: float, storage_gb: float,
                 has_gpu: bool = False, online: bool = True):
        self.name = name
        self.ram_gb = ram_gb
        self.storage_gb = storage_gb
        self.has_gpu = has_gpu
        self.online = online


class ModelSelector:
    @staticmethod
    def estimate_memory(model: str, quant: str = "INT8") -> float:
        info = MODELS[model]
        return round(info["ram_gb"] * QUANTIZATION[quant]["ratio"], 2)
    
    @classmethod
    def recommend(cls, device: Device, task: str = "general") -> Dict:
        candidates = []
        for name, info in MODELS.items():
            mem = cls.estimate_memory(name, "INT8")
            if mem <= device.ram_gb * 0.7:  # 留30%余量
                candidates.append((name, info["quality"], mem))
        
        if not candidates:
            return {"model": None, "reason": "设备算力不足，建议云端"}
        
        if task == "reasoning":
            best = max(candidates, key=lambda x: x[1])
        elif task == "simple":
            best = min(candidates, key=lambda x: x[2])
        else:
            # 平衡：质量/内存
            best = max(candidates, key=lambda x: x[1] / max(x[2], 0.1))
        
        return {"model": best[0], "memory_gb": best[2],
                "quality": best[1], "quant": "INT8"}


# ======================================================================
# 三、端云协同
# ======================================================================

class EdgeCloudRouter:
    SIMPLE = ["你好", "天气", "时间", "翻译", "计算", "是多少"]
    
    def __init__(self, device: Device, local_model: str = None):
        self.device = device
        self.local_model = local_model
        self.stats = {"edge": 0, "cloud": 0, "offline": 0}
    
    def route(self, question: str) -> Dict:
        # 离线 → 端侧或拒答
        if not self.device.online:
            if self.local_model:
                self.stats["offline"] += 1
                return {"route": "edge", "reason": "离线兜底", "model": self.local_model}
            self.stats["offline"] += 1
            return {"route": "error", "reason": "离线且无本地模型"}
        
        simple = any(k in question for k in self.SIMPLE)
        short = len(question) < 30
        
        if simple and short and self.local_model:
            self.stats["edge"] += 1
            return {"route": "edge", "reason": "简单任务本地处理",
                    "model": self.local_model}
        
        self.stats["cloud"] += 1
        return {"route": "cloud", "reason": "复杂任务云端处理",
                "model": "gpt-4"}
    
    def answer(self, question: str) -> Dict:
        decision = self.route(question)
        if decision["route"] == "error":
            return {**decision, "answer": "当前离线，请联网后重试。"}
        if decision["route"] == "edge":
            return {**decision, "answer": f"[端侧{decision['model']}] "
                                          f"回答：{question[:16]}"}
        return {**decision, "answer": f"[云端] 回答：{question[:16]}"}


# ======================================================================
# 四、性能与成本对比
# ======================================================================

def compare_edge_cloud() -> List[Dict]:
    return [
        {"方案": "端侧INT4", "latency_ms": 80, "cost_per_1k": 0.0,
         "privacy": "最高", "quality": "中"},
        {"方案": "端侧INT8", "latency_ms": 120, "cost_per_1k": 0.0,
         "privacy": "最高", "quality": "中高"},
        {"方案": "云端API", "latency_ms": 600, "cost_per_1k": 0.002,
         "privacy": "依赖服务商", "quality": "高"},
    ]


def demo():
    print("=" * 66)
    print("📱 端侧Agent轻量化演示")
    print("=" * 66)
    
    print("\n[1] 量化估算（phi3-mini 3.8B）：")
    for q in QUANTIZATION:
        mem = ModelSelector.estimate_memory("phi3-mini", q)
        print(f"   {q:6s} → {mem}GB（{QUANTIZATION[q]['note']}）")
    
    print("\n[2] 设备选型：")
    devices = [
        Device("手机", 6, 64),
        Device("边缘盒子", 8, 128),
        Device("轻薄本", 16, 512, True),
    ]
    for d in devices:
        rec = ModelSelector.recommend(d, "balanced")
        print(f"   {d.name}（RAM{d.ram_gb}G）→ {rec}")
    
    print("\n[3] 端云协同：")
    phone = Device("手机", 6, 64, online=True)
    router = EdgeCloudRouter(phone, local_model="qwen2-1.5b")
    for q in ["你好", "翻译这段话", "请深度分析这份复杂报告并给出完整方案"]:
        r = router.answer(q)
        print(f"   {q[:16]}... → {r['route']}（{r['reason']}）")
    
    print("\n[4] 离线降级：")
    offline = Device("手机", 6, 64, online=False)
    router_off = EdgeCloudRouter(offline, local_model="qwen2-0.5b")
    print(f"   离线：{router_off.answer('你好')}")
    router_none = EdgeCloudRouter(offline, local_model=None)
    print(f"   无本地模型：{router_none.answer('你好')}")
    
    print("\n[5] 性能成本对比：")
    for row in compare_edge_cloud():
        print(f"   {row['方案']:8s} 延迟{row['latency_ms']}ms "
              f"成本¥{row['cost_per_1k']}/1k 隐私{row['privacy']} 质量{row['quality']}")


if __name__ == "__main__":
    demo()
