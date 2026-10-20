#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第20篇配套完整项目代码 · knowledge_base/kb_core.py
本地私有知识库核心：切片 → 向量化 → 本地存储 → 语义检索

两阶段（文章第二章）：
  阶段一：文档入库（离线）
  阶段二：智能问答（在线检索）
==========================================================================
"""

import json
import os
import re
from typing import Any, Dict, List

import numpy as np

from config import (
    KB_DIR, KB_STORE_PATH, UPLOAD_DOC_PATH,
    KB_CHUNK_SIZE, KB_CHUNK_OVERLAP, EMBED_MODEL_NAME,
    USE_MOCK, MODEL_API_KEY, MODEL_BASE_URL,
)


os.makedirs(KB_DIR, exist_ok=True)
os.makedirs(UPLOAD_DOC_PATH, exist_ok=True)


class LocalKnowledgeBase:
    """本地私有知识库"""
    
    def __init__(self):
        self.store = self.load_store()
        self._embed_client = None
        if not USE_MOCK:
            try:
                from openai import OpenAI
                self._embed_client = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)
            except ImportError:
                self._embed_client = None
    
    # ---------------- 存储 ----------------
    def load_store(self) -> Dict[str, Any]:
        if os.path.exists(KB_STORE_PATH):
            try:
                with open(KB_STORE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "doc_list" in data:
                    return data
            except (json.JSONDecodeError, OSError):
                pass
        return {"doc_list": []}
    
    def save_store(self):
        os.makedirs(KB_DIR, exist_ok=True)
        with open(KB_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.store, f, ensure_ascii=False, indent=2)
    
    # ---------------- 切片 ----------------
    def split_text(self, text: str) -> List[str]:
        """长文本智能切片（重叠切割）"""
        text = re.sub(r"\n{3,}", "\n\n", text.strip())
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + KB_CHUNK_SIZE, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(text):
                break
            start = end - KB_CHUNK_OVERLAP
        return chunks
    
    # ---------------- 向量化 ----------------
    def get_embedding(self, text: str) -> List[float]:
        if self._embed_client is not None:
            resp = self._embed_client.embeddings.create(
                model=EMBED_MODEL_NAME, input=text
            )
            return resp.data[0].embedding
        return self._mock_embedding(text)
    
    @staticmethod
    def _mock_embedding(text: str, dim: int = 256) -> List[float]:
        """确定性伪向量：字符bigram哈希，语义相近→向量相近"""
        vec = np.zeros(dim, dtype=np.float32)
        t = text.lower()
        for i in range(len(t) - 1):
            h = hash(t[i:i+2])
            vec[abs(h) % dim] += 1.0 if h >= 0 else -1.0
        norm = np.linalg.norm(vec) or 1.0
        return (vec / norm).tolist()
    
    # ---------------- 入库 ----------------
    def add_doc_file(self, file_path: str) -> str:
        """读取文档 → 切片 → 向量化 → 入库"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"文档读取失败：{e}"
        
        chunks = self.split_text(content)
        if not chunks:
            return "文档内容为空，未入库"
        
        base = os.path.basename(file_path)
        # 去重：同源同名覆盖旧数据
        self.store["doc_list"] = [d for d in self.store["doc_list"] if d.get("source") != base]
        
        for idx, chunk in enumerate(chunks):
            self.store["doc_list"].append({
                "source": base,
                "chunk_idx": idx,
                "content": chunk,
                "vector": self.get_embedding(chunk),
            })
        
        self.save_store()
        return f"文档入库成功！{base} 共切片 {len(chunks)} 段"
    
    def add_text(self, text: str, source: str = "manual") -> str:
        """直接添加文本"""
        chunks = self.split_text(text)
        for idx, chunk in enumerate(chunks):
            self.store["doc_list"].append({
                "source": source, "chunk_idx": idx,
                "content": chunk, "vector": self.get_embedding(chunk),
            })
        self.save_store()
        return f"文本入库成功！共 {len(chunks)} 段"
    
    # ---------------- 检索 ----------------
    @staticmethod
    def calc_similarity(vec1: List[float], vec2: List[float]) -> float:
        a = np.asarray(vec1, dtype=np.float32)
        b = np.asarray(vec2, dtype=np.float32)
        denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
        return float(np.dot(a, b) / denom)
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """语义检索，返回最匹配内容"""
        docs = self.store.get("doc_list", [])
        if not docs:
            return []
        
        q_vec = self.get_embedding(query)
        scored = []
        for item in docs:
            score = self.calc_similarity(q_vec, item["vector"])
            scored.append({
                "score": round(score, 4),
                "content": item["content"],
                "source": item["source"],
                "chunk_idx": item.get("chunk_idx", 0),
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
    
    def search_as_text(self, query: str, top_k: int = 3) -> str:
        """检索并拼成上下文文本"""
        hits = self.search(query, top_k)
        if not hits:
            return ""
        return "\n\n".join(
            f"[来源：{h['source']} 片段{h['chunk_idx']}]\n{h['content']}"
            for h in hits
        )
    
    # ---------------- 管理 ----------------
    def clear_kb(self) -> str:
        self.store = {"doc_list": []}
        self.save_store()
        return "知识库已清空"
    
    def stats(self) -> Dict[str, Any]:
        docs = self.store.get("doc_list", [])
        sources = sorted({d["source"] for d in docs})
        return {
            "documents": len(sources),
            "sources": sources,
            "chunks": len(docs),
            "embedding_dim": len(docs[0]["vector"]) if docs else 0,
        }


# 全局单例
kb = LocalKnowledgeBase()
