import re
import numpy as np

class RAGEvaluator:
    def __init__(self):
        # 停用词过滤（无意义词汇不参与评分）
        self.stop_words = {"的","了","是","在","我","你","他","和","与","及","等","可以","能够","需要"}

    def extract_key_words(self, text: str) -> list:
        """提取文本核心关键词，过滤停用词"""
        words = re.findall(r"[\u4e00-\u9fa5a-zA-Z0-9]+", text)
        key_words = [w for w in words if w not in self.stop_words and len(w) > 1]
        return list(set(key_words))

    def calc_recall_score(self, query: str, retrieve_content: str) -> float:
        """
        1. 检索覆盖率评分（0-100）
        核心关键词覆盖越多，分数越高
        """
        query_keys = self.extract_key_words(query)
        if not query_keys:
            return 100.0
        retrieve_keys = self.extract_key_words(retrieve_content)
        match_keys = [k for k in query_keys if k in retrieve_keys]
        recall_rate = len(match_keys) / len(query_keys)
        return round(recall_rate * 100, 2)

    def calc_precision_score(self, query: str, retrieve_content: str) -> float:
        """
        2. 语义匹配精准度评分（0-100）
        检索内容有效信息占比，剔除无关冗余内容
        """
        query_keys = self.extract_key_words(query)
        retrieve_keys = self.extract_key_words(retrieve_content)
        if not retrieve_keys:
            return 0.0
        match_keys = [k for k in retrieve_keys if k in query_keys]
        precision_rate = len(match_keys) / len(retrieve_keys)
        return round(precision_rate * 100, 2)

    def calc_complete_score(self, query: str, answer: str) -> float:
        """
        3. 回答完整度评分（0-100）
        判断答案是否覆盖提问核心诉求
        """
        query_keys = self.extract_key_words(query)
        if not query_keys:
            return 100.0
        ans_keys = self.extract_key_words(answer)
        match_num = sum(1 for k in query_keys if k in ans_keys)
        complete_rate = match_num / len(query_keys)
        return round(complete_rate * 100, 2)

    def calc_purity_score(self, answer: str) -> float:
        """
        4. 内容纯净度评分（0-100）
        检测重复语句、冗余内容、无效话术
        """
        lines = [line.strip() for line in answer.split("\n") if line.strip()]
        if not lines:
            return 0.0
        # 计算重复行占比
        unique_lines = list(set(lines))
        purity_rate = len(unique_lines) / len(lines)
        return round(purity_rate * 100, 2)

    def get_grade(self, total_score: float) -> str:
        """分数评级：S/A/B/C/D"""
        if total_score >= 90:
            return "S 顶级优质问答"
        elif total_score >= 80:
            return "A 良好达标"
        elif total_score >= 70:
            return "B 合格可用"
        elif total_score >= 60:
            return "C 一般需优化"
        else:
            return "D 较差存在缺陷"

    def evaluate(self, query: str, retrieve_content: str, answer: str) -> dict:
        """
        一站式综合评分入口
        返回四维分数、总分、评级、优化建议
        """
        # 四大维度打分
        recall_sc = self.calc_recall_score(query, retrieve_content)
        precision_sc = self.calc_precision_score(query, retrieve_content)
        complete_sc = self.calc_complete_score(query, answer)
        purity_sc = self.calc_purity_score(answer)

        # 加权综合总分
        total = (recall_sc * 0.3) + (precision_sc * 0.3) + (complete_sc * 0.25) + (purity_sc * 0.15)
        total = round(total, 2)

        # 智能优化建议
        suggest = []
        if recall_sc < 70:
            suggest.append("检索覆盖率低：存在关键词漏召，建议扩充文档或调整切片大小")
        if precision_sc < 70:
            suggest.append("匹配精度低：检索存在无关内容，建议清洗文档或调高关键词权重")
        if complete_sc < 70:
            suggest.append("回答完整度不足：知识库关键信息缺失，需补充对应文档内容")
        if purity_sc < 70:
            suggest.append("内容纯净度低：回答存在冗余重复，可优化切片重叠参数")
        if not suggest:
            suggest.append("问答质量优秀，无需优化")

        return {
            "检索覆盖率": recall_sc,
            "匹配精准度": precision_sc,
            "回答完整度": complete_sc,
            "内容纯净度": purity_sc,
            "综合总分": total,
            "质量评级": self.get_grade(total),
            "优化建议": suggest
        }

# 全局单例
evaluator = RAGEvaluator()
