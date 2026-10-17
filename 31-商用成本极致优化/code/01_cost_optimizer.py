"""
商用成本极致优化模块
第31篇：API成本控制、缓存节流、模型智能路由
商用接单专属，降低70%以上Token开销
"""
import time
import re

class CommercialCostOptimizer:
    def __init__(self):
        # 缓存字典：key=问题，value=(答案, 时间戳)
        self.cache_map = {}
        # 缓存有效期：24小时自动刷新（企业场景足够稳定）
        self.cache_ttl = 86400
        # 无效提问拦截词库
        self.useless_pattern = [
            "^你好$","^您好$","^在吗$","^哈喽$","^hi$","^hello$",
            "谢谢$","感谢$","嗯嗯$","好的$"
        ]
        # 长短句阈值
        self.short_query_len = 6

    def is_useless_query(self, query: str) -> bool:
        """判断是否为无效闲聊提问，直接拦截不调用API"""
        q = query.strip().lower()
        for p in self.useless_pattern:
            if re.match(p, q):
                return True
        # 过短无意义提问拦截
        if len(q) <= self.short_query_len and not any(key in q for key in ["什么","怎么","如何","为什么"]):
            return True
        return False

    def check_cache(self, query: str) -> str | None:
        """
        查询本地缓存
        命中返回缓存答案，未命中返回None
        """
        now = time.time()
        if query in self.cache_map:
            ans, ts = self.cache_map[query]
            if now - ts < self.cache_ttl:
                return ans
        return None

    def set_cache(self, query: str, answer: str):
        """写入缓存，高频问题复用"""
        self.cache_map[query] = (answer, time.time())

    def smart_model_route(self, query: str, has_kb_result: bool) -> str:
        """
        智能模型路由（核心省钱逻辑）
        simple：轻量低价模型
        premium：高精度高价模型
        """
        # 无知识库内容、简单闲聊、短句问题 → 用便宜模型
        if not has_kb_result or len(query) < 15:
            return "simple"
        # 长问题、需要知识库推理 → 用高端模型
        return "premium"

# 全局商用成本优化单例
cost_opt = CommercialCostOptimizer()
