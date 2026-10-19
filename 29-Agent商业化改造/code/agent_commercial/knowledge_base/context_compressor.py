#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第25篇配套完整项目代码 · knowledge_base/context_compressor.py
RAG 自适应上下文压缩（四层级本地压缩，零模型调用）

  1. 冗余剔除：清理检索格式标签、重复语句、冗余换行
  2. 权重筛选：优先保留高综合得分切片
  3. 自适应裁剪：按 Token 阈值动态压缩，不固定截断字数
  4. 完整性兜底：句末标点截断，关键语句不被拦腰切断
==========================================================================
"""

import re


class ContextCompressor:
    def __init__(self):
        # 正则匹配检索输出中的冗余格式文本
        self.score_pattern = re.compile(r"（综合匹配分：[\d\.\-]+(?:，[^）]*)?）")
        self.source_pattern = re.compile(r"来源文档：.+?\n")
        self.prefix_pattern = re.compile(r"【高精度知识库检索结果】\n")
        self.chunk_label_pattern = re.compile(r"\n片段\d+(?:（[^）]*）)?\n")
        self.citation_label_pattern = re.compile(r"\[引用\d+\]\s*")
    
    # ---------------- 1. 冗余剔除 ----------------
    def clean_rag_format(self, text: str) -> str:
        """清理RAG检索自带冗余格式内容"""
        text = self.prefix_pattern.sub("", text)
        text = self.chunk_label_pattern.sub("\n", text)
        text = self.score_pattern.sub("", text)
        text = self.source_pattern.sub("", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{2,}", "\n", text)
        return text.strip()
    
    def clean_citation_format(self, text: str) -> str:
        """清理带引用标记的检索上下文格式（保留 [引用N] 与来源，供溯源使用）"""
        text = re.sub(r"【参考知识库片段（带溯源）】", "", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{2,}", "\n", text)
        return text.strip()
    
    def remove_repeat_sentence(self, text: str) -> str:
        """去除重复语句/重复行"""
        lines = text.split("\n")
        seen = set()
        unique = []
        for line in lines:
            key = line.strip()
            if not key:
                continue
            if key in seen:
                continue
            seen.add(key)
            unique.append(key)
        return "\n".join(unique)
    
    # ---------------- 2. 权重筛选 ----------------
    @staticmethod
    def filter_by_score(items, min_score: float = 0.0):
        """按综合得分过滤低价值片段（items: [{'total_score':...}]）"""
        return [x for x in items if x.get("total_score", x.get("score", 0)) >= min_score]
    
    # ---------------- 3. 自适应裁剪 ----------------
    def adaptive_trim(self, text: str, max_token: int = 1800) -> str:
        """按字符近似Token换算（1中文≈2Token），保证句子完整"""
        max_char = int(max_token / 2)
        if len(text) <= max_char:
            return text
        
        end_punct = {"。", "！", "？", ".", "!", "?", "；", ";"}
        trim_text = text[:max_char]
        
        # 从末尾往前找完整句结尾，防止断句
        last_end_idx = 0
        for idx, ch in enumerate(trim_text):
            if ch in end_punct:
                last_end_idx = idx + 1
        
        if last_end_idx > 0:
            trim_text = trim_text[:last_end_idx]
        else:
            # 无标点兜底，按段落截断
            trim_text = trim_text.rsplit("\n", 1)[0] or trim_text
        
        return trim_text.strip()
    
    # ---------------- 4. 一站式压缩 ----------------
    def compress(self, rag_context: str, max_token: int = 1800,
                 citation_mode: bool = False) -> str:
        """一站式上下文压缩入口
        
        :param rag_context: 原始检索拼接文本
        :param max_token: 模型最大接收 Token
        :param citation_mode: 是否带引用标记（True时用引用清理规则）
        """
        text = (self.clean_citation_format(rag_context)
                if citation_mode else self.clean_rag_format(rag_context))
        text = self.remove_repeat_sentence(text)
        text = self.adaptive_trim(text, max_token)
        return text
    
    # ---------------- 统计辅助 ----------------
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """估算Token（中文≈2倍字符）"""
        return int(len(text) * 1.5)
    
    def stats(self, before: str, after: str) -> dict:
        tb, ta = self.estimate_tokens(before), self.estimate_tokens(after)
        return {
            "chars_before": len(before), "chars_after": len(after),
            "tokens_before": tb, "tokens_after": ta,
            "reduction": f"{(1 - ta / tb) * 100:.1f}%" if tb else "0%",
        }


compressor = ContextCompressor()
