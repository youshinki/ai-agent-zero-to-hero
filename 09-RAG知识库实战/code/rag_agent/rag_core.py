#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第9篇配套完整项目代码 · rag_core.py
RAG知识库核心：加载 → 分块 → 向量化 → 存储 → 检索
==========================================================================

实现标准RAG五步法（文章第2章）：
  1. 文档加载
  2. 文本分块（Chunk）
  3. 向量化嵌入（Embedding）
  4. 相似度检索
  5. 增强生成（在 agent_core 中完成）
==========================================================================
"""

import math
import os
import re
from typing import (Dict, List)

from config import (
    USE_MOCK, EMBED_MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL,
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, VERBOSE,
)


class RAGCore:
    """RAG知识库核心"""
    
    def __init__(self):
        self.chunks: List[str] = []            # 文本块
        self.metadata: List[Dict] = []         # 每块的元信息（来源）
        self.embeddings: List[List[float]] = []  # 向量（模拟时为稀疏向量）
        self.index = None                      # FAISS索引（真实模式）
        self.use_real_embedding = not USE_MOCK
        self._init_embedding()
    
    # ------------------------------------------------------------------
    # 1. 加载本地文档（支持 txt / md / pdf / docx）
    # ------------------------------------------------------------------
    def load_doc(self, file_path: str) -> str:
        """加载本地文档为纯文本"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in (".txt", ".md"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        
        if ext == ".pdf":
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(file_path)
                return "\n".join((p.extract_text() or "") for p in reader.pages)
            except ImportError:
                return f"[PDF] {file_path}（未安装PyPDF2，返回占位文本）"
        
        if ext == ".docx":
            try:
                from docx import Document
                doc = Document(file_path)
                return "\n".join(p.text for p in doc.paragraphs)
            except ImportError:
                return f"[DOCX] {file_path}（未安装python-docx，返回占位文本）"
        
        # 未知格式按文本读
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    
    # ------------------------------------------------------------------
    # 2. 文本分块（重叠切割，保证上下文连贯）
    # ------------------------------------------------------------------
    def split_chunk(self, text: str, source: str = "unknown") -> List[str]:
        """按固定窗口+重叠切分文本"""
        text = re.sub(r"\n{3,}", "\n\n", text.strip())
        chunks = []
        start = 0
        length = len(text)
        
        while start < length:
            end = min(start + CHUNK_SIZE, length)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
                self.metadata.append({"source": source, "start": start, "end": end})
            if end >= length:
                break
            # 重叠切割：下一块从 end - overlap 开始
            start = end - CHUNK_OVERLAP
        
        self.chunks.extend(chunks)
        return chunks
    
    # ------------------------------------------------------------------
    # 3. 向量化嵌入
    # ------------------------------------------------------------------
    def _init_embedding(self):
        """初始化嵌入客户端"""
        self._embed_client = None
        if self.use_real_embedding:
            try:
                from openai import OpenAI
                self._embed_client = OpenAI(
                    api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL
                )
            except ImportError:
                self.use_real_embedding = False
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本向量
        
        真实模式：调用 Embedding API
        模拟模式：用字符n-gram哈希生成确定性的稠密向量（语义近似效果）
        """
        if self.use_real_embedding and self._embed_client:
            resp = self._embed_client.embeddings.create(
                input=text, model=EMBED_MODEL_NAME
            )
            return resp.data[0].embedding
        return self._mock_embedding(text)
    
    @staticmethod
    def _mock_embedding(text: str, dim: int = 256) -> List[float]:
        """确定性伪向量：相同/相近文本得到相近向量
        
        做法：字符bigram哈希到固定维度，归一化。
        """
        vec = [0.0] * dim
        text = text.lower()
        for i in range(len(text) - 1):
            gram = text[i:i+2]
            h = hash(gram)
            idx = abs(h) % dim
            sign = 1.0 if h >= 0 else -1.0
            vec[idx] += sign
        # 归一化
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]
    
    # ------------------------------------------------------------------
    # 4. 构建向量库
    # ------------------------------------------------------------------
    def build_vector_store(self):
        """向量化所有块并构建索引"""
        self.embeddings = [self.get_embedding(c) for c in self.chunks]
        
        # 若安装了FAISS，使用FAISS索引
        try:
            import numpy as np
            import faiss
            arr = np.array(self.embeddings).astype("float32")
            self.index = faiss.IndexFlatL2(arr.shape[1])
            self.index.add(arr)
            if VERBOSE:
                print(f"  🗂️ FAISS索引构建完成（{arr.shape[0]}条，{arr.shape[1]}维）")
        except ImportError:
            self.index = None
            if VERBOSE:
                print(f"  🗂️ 纯Python向量库构建完成（{len(self.embeddings)}条，未安装faiss）")
    
    # ------------------------------------------------------------------
    # 5. 相似度检索
    # ------------------------------------------------------------------
    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1.0
        nb = math.sqrt(sum(y * y for y in b)) or 1.0
        return dot / (na * nb)
    
    def search_relevant(self, query: str, top_k: int = TOP_K,
                        return_scores: bool = False) -> str:
        """检索最相关的文本块，拼接返回"""
        if not self.chunks:
            return ""
        
        q_emb = self.get_embedding(query)
        
        # FAISS 检索
        if self.index is not None:
            try:
                import numpy as np
                q = np.array([q_emb]).astype("float32")
                distances, indices = self.index.search(q, min(top_k, len(self.chunks)))
                selected = [self.chunks[i] for i in indices[0] if i >= 0]
                if return_scores:
                    return selected
                return "\n\n".join(selected)
            except Exception:
                pass
        
        # 纯Python余弦相似度检索
        scored = []
        for i, emb in enumerate(self.embeddings):
            scored.append((self._cosine(q_emb, emb), i))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]
        
        if return_scores:
            return [(self.chunks[i], round(score, 4), self.metadata[i]) for score, i in top]
        
        return "\n\n".join(self.chunks[i] for _, i in top)
    
    # ------------------------------------------------------------------
    # 初始化知识库（一站式）
    # ------------------------------------------------------------------
    def init_knowledge_base(self, doc_paths, announce: bool = True):
        """加载文档 → 分块 → 构建向量库"""
        if isinstance(doc_paths, str):
            doc_paths = [doc_paths]
        
        if announce:
            print("=" * 55)
            print("📚 正在初始化RAG知识库...")
        
        total_chars = 0
        for path in doc_paths:
            if not os.path.exists(path):
                print(f"  ⚠️ 文档不存在，跳过：{path}")
                continue
            if announce:
                print(f"  📄 加载文档：{path}")
            text = self.load_doc(path)
            total_chars += len(text)
            self.split_chunk(text, source=os.path.basename(path))
        
        if announce:
            print(f"  ✂️ 文本分块完成：{len(self.chunks)} 个块（总{total_chars}字）")
        
        self.build_vector_store()
        
        if announce:
            print("✅ 知识库初始化完成！")
            print("=" * 55)
        return self
    
    def stats(self) -> Dict:
        return {
            "documents": len(set(m["source"] for m in self.metadata)),
            "chunks": len(self.chunks),
            "embedding_dim": len(self.embeddings[0]) if self.embeddings else 0,
        }
