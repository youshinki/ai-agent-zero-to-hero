#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第27篇配套完整项目代码 · knowledge_base/rag_evaluator.py
RAG 智能评分体系（四维量化评估，本地算法零成本）

四维评分：
  1. 检索覆盖率（权重30%）：核心关键词覆盖
  2. 匹配精准度（权重30%）：有效信息占比
  3. 回答完整度（权重25%）：是否覆盖提问诉求
  4. 内容纯净度（权重15%）：重复/冗余检测
==========================================================================
"""

import re


class RAGEvaluator:
    def __init__(self):
        # 停用词（不参与评分）
        self.stop_words = {
            "的", "了", "是", "在", "我", "你", "他", "她", "它", "和", "与", "及",
            "等", "可以", "能够", "需要", "什么", "哪些", "如何", "怎么", "多少",
            "请问", "一下", "是否", "这个", "那个", "以及", "还是", "一个",
        }
    
    # ---------------- 关键词提取 ----------------
    def extract_key_words(self, text: str) -> list:
        """提取核心关键词，过滤停用词与单字"""
        words = re.findall(r"[\u4e00-\u9fa5a-zA-Z0-9]+", text)
        keys = [w for w in words if len(w) > 1 and w not in self.stop_words]
        # 长词再拆出2-4字子词，提升中文匹配召回
        expanded = []
        for w in keys:
            expanded.append(w)
            if len(w) > 4:
                expanded.extend(w[i:i+2] for i in range(len(w) - 1))
        return list(set(expanded))
    
    # ---------------- 四维评分 ----------------
    def calc_recall_score(self, query: str, retrieve_content: str) -> float:
        """1. 检索覆盖率：提问关键词被检索内容覆盖的比例"""
        query_keys = self.extract_key_words(query)
        if not query_keys:
            return 100.0
        retrieve_keys = set(self.extract_key_words(retrieve_content))
        matched = sum(1 for k in query_keys if k in retrieve_keys)
        return round(matched / len(query_keys) * 100, 2)
    
    def calc_precision_score(self, query: str, retrieve_content: str) -> float:
        """2. 匹配精准度：检索内容中有效信息占比"""
        query_keys = set(self.extract_key_words(query))
        retrieve_keys = self.extract_key_words(retrieve_content)
        if not retrieve_keys:
            return 0.0
        matched = sum(1 for k in retrieve_keys if k in query_keys)
        return round(matched / len(retrieve_keys) * 100, 2)
    
    def calc_complete_score(self, query: str, answer: str) -> float:
        """3. 回答完整度：答案覆盖提问诉求的比例"""
        query_keys = self.extract_key_words(query)
        if not query_keys:
            return 100.0
        ans_keys = set(self.extract_key_words(answer))
        matched = sum(1 for k in query_keys if k in ans_keys)
        return round(matched / len(query_keys) * 100, 2)
    
    def calc_purity_score(self, answer: str) -> float:
        """4. 内容纯净度：非重复行占比"""
        lines = [line.strip() for line in answer.split("\n") if line.strip()]
        if not lines:
            return 0.0
        return round(len(set(lines)) / len(lines) * 100, 2)
    
    # ---------------- 评级与建议 ----------------
    @staticmethod
    def get_grade(total_score: float) -> str:
        if total_score >= 90:
            return "S 顶级优质问答"
        if total_score >= 80:
            return "A 良好达标"
        if total_score >= 70:
            return "B 合格可用"
        if total_score >= 60:
            return "C 一般需优化"
        return "D 较差存在缺陷"
    
    def evaluate(self, query: str, retrieve_content: str, answer: str) -> dict:
        """一站式综合评分"""
        recall = self.calc_recall_score(query, retrieve_content)
        precision = self.calc_precision_score(query, retrieve_content)
        complete = self.calc_complete_score(query, answer)
        purity = self.calc_purity_score(answer)
        
        total = round(
            recall * 0.30 + precision * 0.30 + complete * 0.25 + purity * 0.15, 2
        )
        
        suggest = []
        if recall < 70:
            suggest.append("检索覆盖率低：存在关键词漏召，建议扩充文档或调整切片大小")
        if precision < 70:
            suggest.append("匹配精度低：检索存在无关内容，建议清洗文档或调高关键词权重")
        if complete < 70:
            suggest.append("回答完整度不足：知识库关键信息缺失，需补充对应文档内容")
        if purity < 70:
            suggest.append("内容纯净度低：回答存在冗余重复，可优化切片重叠参数")
        if not suggest:
            suggest.append("问答质量优秀，无需优化")
        
        return {
            "检索覆盖率": recall,
            "匹配精准度": precision,
            "回答完整度": complete,
            "内容纯净度": purity,
            "综合总分": total,
            "质量评级": self.get_grade(total),
            "优化建议": suggest,
        }


evaluator = RAGEvaluator()
