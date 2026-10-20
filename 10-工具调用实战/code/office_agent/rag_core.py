#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第10篇配套完整项目代码 · rag_core.py
沿用第9篇的RAG知识库检索能力
==========================================================================
"""

import math
import os
import re
from typing import Dict, List

from config import (CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, VERBOSE)


class RAGCore:
    """RAG知识库核心（加载 → 分块 → 向量化 → 检索）"""
    
    def __init__(self):
        self.chunks: List[str] = []
        self.metadata: List[Dict] = []
        self.embeddings: List[List[float]] = []
    
    # ----- 1. 加载文档 -----
    def load_doc(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".txt", ".md"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        if ext == ".pdf":
            try:
                from PyPDF2 import PdfReader
                return "\n".join((p.extract_text() or "") for p in PdfReader(file_path).pages)
            except ImportError:
                return f"[PDF] {file_path}"
        if ext == ".docx":
            try:
                from docx import Document
                return "\n".join(p.text for p in Document(file_path).paragraphs)
            except ImportError:
                return f"[DOCX] {file_path}"
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    
    # ----- 2. 分块 -----
    def split_chunk(self, text: str, source: str = "unknown") -> List[str]:
        text = re.sub(r"\n{3,}", "\n\n", text.strip())
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
                self.metadata.append({"source": source, "start": start, "end": end})
            if end >= len(text):
                break
            start = end - CHUNK_OVERLAP
        self.chunks.extend(chunks)
        return chunks
    
    # ----- 3. 向量化（模拟：字符bigram哈希）-----
    @staticmethod
    def _embed(text: str, dim: int = 256) -> List[float]:
        vec = [0.0] * dim
        t = text.lower()
        for i in range(len(t) - 1):
            h = hash(t[i:i+2])
            vec[abs(h) % dim] += 1.0 if h >= 0 else -1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]
    
    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        return sum(x * y for x, y in zip(a, b)) / (
            (math.sqrt(sum(x * x for x in a)) or 1.0) *
            (math.sqrt(sum(y * y for y in b)) or 1.0)
        )
    
    # ----- 4. 构建向量库 -----
    def build_vector_store(self):
        self.embeddings = [self._embed(c) for c in self.chunks]
        if VERBOSE:
            print(f"  🗂️ 向量库构建完成（{len(self.embeddings)}条）")
    
    # ----- 5. 检索 -----
    def search_relevant(self, query: str, top_k: int = TOP_K,
                        return_scores: bool = False):
        if not self.chunks:
            return [] if return_scores else ""
        q = self._embed(query)
        scored = [(self._cosine(q, e), i) for i, e in enumerate(self.embeddings)]
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]
        if return_scores:
            return [(self.chunks[i], round(s, 4), self.metadata[i]) for s, i in top]
        return "\n\n".join(self.chunks[i] for _, i in top)
    
    # ----- 一站式初始化 -----
    def init_knowledge_base(self, doc_paths, announce: bool = True):
        if isinstance(doc_paths, str):
            doc_paths = [doc_paths]
        if announce:
            print("=" * 55)
            print("📚 初始化RAG知识库...")
        for path in doc_paths:
            if not os.path.exists(path):
                print(f"  ⚠️ 文档不存在：{path}")
                continue
            self.split_chunk(self.load_doc(path), os.path.basename(path))
        self.build_vector_store()
        if announce:
            print(f"✅ 知识库就绪：{len(self.chunks)}个块")
        return self
