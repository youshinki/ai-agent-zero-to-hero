# 第71篇配套代码：向量库选型与性能调优
# 索引策略、分片、过滤查询、召回瓶颈排查
# 运行：python 01_vector_db_optimization.py

import numpy as np
import time
from typing import List, Dict, Optional

# ========== 向量库性能测试 ==========
class VectorDBBenchmark:
    """向量库性能基准测试"""
    
    def __init__(self, dim=768):
        self.dim = dim
        self.vectors = []
        self.ids = []
    
    def generate_data(self, count=10000):
        """生成测试数据"""
        np.random.seed(42)
        self.vectors = np.random.randn(count, self.dim).astype(np.float32)
        # 归一化
        self.vectors = self.vectors / np.linalg.norm(self.vectors, axis=1, keepdims=True)
        self.ids = [f"doc_{i}" for i in range(count)]
        return {"count": count, "dim": self.dim}
    
    def brute_force_search(self, query, top_k=10):
        """暴力搜索（基准）"""
        scores = np.dot(self.vectors, query)
        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [(self.ids[i], float(scores[i])) for i in top_indices]

# ========== 索引策略对比 ==========
class IndexStrategies:
    """索引策略对比"""
    
    @staticmethod
    def compare_strategies():
        return {
            "Flat（暴力搜索）": {
                "原理": "全量计算相似度",
                "召回率": "100%",
                "速度": "慢（10万级1秒）",
                "内存": "高",
                "适合": "数据量<10万，高精度要求"
            },
            "IVF（倒排文件）": {
                "原理": "聚类分区，只搜索最近簇",
                "召回率": "95-99%",
                "速度": "快（10万级0.1秒）",
                "内存": "中",
                "适合": "大规模数据，可接受少量精度损失"
            },
            "HNSW（分层导航图）": {
                "原理": "多层级图结构搜索",
                "召回率": "98-100%",
                "速度": "极快（10万级0.01秒）",
                "内存": "高",
                "适合": "高性能场景，精度和速度平衡"
            },
            "PQ（乘积量化）": {
                "原理": "向量压缩，减少存储",
                "召回率": "85-95%",
                "速度": "快",
                "内存": "低（压缩80%）",
                "适合": "内存受限的大规模场景"
            }
        }

# ========== 分片策略 ==========
class ShardingStrategy:
    """分片策略"""
    
    @staticmethod
    def get_strategies():
        return {
            "按ID哈希分片": {
                "原理": "doc_id哈希取模分配到不同分片",
                "优点": "数据均匀分布",
                "缺点": "查询需要广播到所有分片",
                "适合": "写入密集型"
            },
            "按内容语义分片": {
                "原理": "相似内容分配到同一分片",
                "优点": "查询只需访问少数分片",
                "缺点": "可能存在数据倾斜",
                "适合": "查询密集型"
            },
            "按时序分片": {
                "原理": "按时间范围划分",
                "优点": "时间范围查询高效",
                "缺点": "热点集中在最新分片",
                "适合": "时序数据"
            }
        }

# ========== 过滤查询优化 ==========
class FilterOptimization:
    """过滤查询优化"""
    
    @staticmethod
    def pre_filter_vs_post_filter():
        return """
# 过滤策略对比

## 1. 后过滤（Post-filter）
流程：检索 → 过滤
优点：简单实现
缺点：可能返回不足top_k结果
适用：过滤条件少，过滤率低

## 2. 预过滤（Pre-filter）
流程：过滤 → 检索
优点：保证返回top_k结果
缺点：需要额外索引
适用：频繁使用固定过滤条件

## 3. 混合过滤（Hybrid）
流程：检索时带上过滤条件
原理：利用向量库的filter功能
优点：精度和性能平衡
适用：大多数场景
"""

# ========== 召回瓶颈排查 ==========
class RecallDebugger:
    """召回问题排查"""
    
    @staticmethod
    def diagnose_recall_issue(symptom):
        diagnoses = {
            "返回结果少": [
                "检查top_k参数是否太小",
                "检查向量维度是否匹配",
                "检查数据是否已正确索引",
                "检查过滤条件是否过于严格"
            ],
            "结果相关性差": [
                "检查embedding模型是否合适",
                "检查分块策略是否合理",
                "检查是否有数据噪声",
                "尝试使用重排序提升精度"
            ],
            "查询速度慢": [
                "检查是否使用了合适的索引",
                "考虑增加集群节点",
                "优化查询QPS",
                "检查是否有慢查询"
            ],
            "内存占用高": [
                "考虑使用PQ量化",
                "检查是否有数据泄露",
                "优化索引参数",
                "考虑分片存储"
            ]
        }
        return diagnoses.get(symptom, ["未知问题，建议查看日志"])

if __name__ == "__main__":
    print("=" * 60)
    print("🗄️ 向量库选型与性能调优")
    print("=" * 60)
    
    # 基准测试
    bm = VectorDBBenchmark(dim=768)
    info = bm.generate_data(10000)
    print(f"\n📊 测试数据：{info['count']}条，维度{info['dim']}")
    
    query = np.random.randn(768).astype(np.float32)
    query = query / np.linalg.norm(query)
    
    start = time.time()
    results = bm.brute_force_search(query, top_k=5)
    elapsed = time.time() - start
    print(f"\n暴力搜索耗时：{elapsed*1000:.2f}ms")
    print(f"Top 5结果：{results[:3]}...")
    
    # 索引策略对比
    print("\n" + "=" * 60)
    print("📋 索引策略对比")
    print("=" * 60)
    for name, info in IndexStrategies.compare_strategies().items():
        print(f"\n  🔷 {name}")
        for k, v in info.items():
            print(f"    {k}：{v}")
    
    # 分片策略
    print("\n" + "=" * 60)
    print("🔀 分片策略")
    print("=" * 60)
    for name, info in ShardingStrategy.get_strategies().items():
        print(f"\n  🔷 {name}")
        for k, v in info.items():
            print(f"    {k}：{v}")
    
    # 召回问题排查
    print("\n" + "=" * 60)
    print("🔍 召回问题排查")
    print("=" * 60)
    symptoms = ["返回结果少", "结果相关性差", "查询速度慢"]
    for s in symptoms:
        print(f"\n  ❓ {s}")
        for d in RecallDebugger.diagnose_recall_issue(s):
            print(f"    • {d}")
