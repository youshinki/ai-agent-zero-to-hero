#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第21篇配套完整项目代码 · knowledge_base/kb_core.py
增量知识库核心：文件指纹 + 增量差分更新 + 自动清理
==========================================================================

核心逻辑（文章第二章）：
  1. 指纹记录：入库时保存每个文件的 MD5
  2. 变动监测：对比新旧 MD5
  3. 差分处理：未改跳过，仅处理新增/修改
  4. 增量入库：只对变动内容切片向量化
  5. 自动清理：删除过期片段/废弃文档向量
==========================================================================
"""

import hashlib
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
from .parse_doc import parse_file_to_text
from .text_cleaner import cleaner


os.makedirs(KB_DIR, exist_ok=True)
os.makedirs(UPLOAD_DOC_PATH, exist_ok=True)


def get_file_md5(file_path: str) -> str:
    """获取文件MD5指纹，用于监测文件变动"""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


class LocalKnowledgeBase:
    """支持增量更新的本地知识库"""
    
    def __init__(self):
        self.store = self.load_store()
        self._embed_client = None
        if not USE_MOCK:
            try:
                from openai import OpenAI
                self._embed_client = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)
            except ImportError:
                pass
    
    # ---------------- 存储（兼容旧版本） ----------------
    def load_store(self) -> Dict[str, Any]:
        if os.path.exists(KB_STORE_PATH):
            try:
                with open(KB_STORE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data.setdefault("file_fingerprint", {})
                data.setdefault("doc_list", [])
                return data
            except (json.JSONDecodeError, OSError):
                pass
        return {"doc_list": [], "file_fingerprint": {}}
    
    def save_store(self):
        os.makedirs(KB_DIR, exist_ok=True)
        with open(KB_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.store, f, ensure_ascii=False, indent=2)
    
    # ---------------- 清洗 + 智能切片 ----------------
    def split_text(self, text: str) -> List[str]:
        """智能清洗 + 语义切片（第23篇升级）"""
        return cleaner.clean_and_split(
            text, chunk_size=KB_CHUNK_SIZE, overlap=KB_CHUNK_OVERLAP
        )
    
    def get_embedding(self, text: str) -> List[float]:
        if self._embed_client is not None:
            resp = self._embed_client.embeddings.create(model=EMBED_MODEL_NAME, input=text)
            return resp.data[0].embedding
        return self._mock_embedding(text)
    
    @staticmethod
    def _mock_embedding(text: str, dim: int = 256) -> List[float]:
        vec = np.zeros(dim, dtype=np.float32)
        t = text.lower()
        for i in range(len(t) - 1):
            h = hash(t[i:i+2])
            vec[abs(h) % dim] += 1.0 if h >= 0 else -1.0
        norm = np.linalg.norm(vec) or 1.0
        return (vec / norm).tolist()
    
    # ---------------- 增量更新核心 ----------------
    def clean_file_vector(self, file_name: str) -> str:
        """清理指定文件所有旧向量数据"""
        old_count = len(self.store["doc_list"])
        self.store["doc_list"] = [d for d in self.store["doc_list"] if d.get("source") != file_name]
        self.store["file_fingerprint"].pop(file_name, None)
        self.save_store()
        return f"清理旧向量片段{old_count - len(self.store['doc_list'])}段"
    
    def single_file_increment_update(self, file_path: str) -> Dict[str, Any]:
        """单文件增量更新"""
        if not os.path.exists(file_path):
            msg = self.clean_file_vector(os.path.basename(file_path))
            return {"status": "deleted", "file": os.path.basename(file_path), "message": msg}
        
        file_name = os.path.basename(file_path)
        new_md5 = get_file_md5(file_path)
        
        # 1. 未改动 → 跳过
        if file_name in self.store["file_fingerprint"] and \
                self.store["file_fingerprint"][file_name] == new_md5:
            return {"status": "unchanged", "file": file_name,
                    "message": f"【无需更新】文件无变动：{file_name}"}
        
        # 2. 已修改 → 清理旧向量
        self.clean_file_vector(file_name)
        
        # 3. 通用解析（支持 pdf/docx/txt/md）
        content = parse_file_to_text(file_path)
        if content.startswith("文档解析失败") or content.startswith("暂不支持解析"):
            return {"status": "failed", "file": file_name, "message": f"【解析失败】{file_name}：{content}"}
        chunks = self.split_text(content)
        for idx, chunk in enumerate(chunks):
            self.store["doc_list"].append({
                "source": file_name, "chunk_idx": idx,
                "content": chunk, "vector": self.get_embedding(chunk),
            })
        
        # 4. 更新指纹
        self.store["file_fingerprint"][file_name] = new_md5
        self.save_store()
        return {"status": "updated", "file": file_name,
                "message": f"【增量更新成功】{file_name}，新增切片{len(chunks)}段",
                "chunks": len(chunks)}
    
    def scan_all_update(self) -> List[Dict[str, Any]]:
        """扫描全部文档，全自动增量更新"""
        log = []
        for fname in sorted(os.listdir(UPLOAD_DOC_PATH)):
            if fname.endswith((".txt", ".md", ".pdf", ".docx")):
                log.append(self.single_file_increment_update(
                    os.path.join(UPLOAD_DOC_PATH, fname)))
        return log
    
    def cleanup_orphans(self) -> str:
        """清理磁盘上已删除文件的残留向量"""
        disk_files = {f for f in os.listdir(UPLOAD_DOC_PATH)
                      if f.endswith((".txt", ".md", ".pdf", ".docx"))}
        orphans = [src for src in self.store["file_fingerprint"] if src not in disk_files]
        cleaned = 0
        for src in orphans:
            before = len(self.store["doc_list"])
            self.store["doc_list"] = [d for d in self.store["doc_list"] if d.get("source") != src]
            cleaned += before - len(self.store["doc_list"])
            del self.store["file_fingerprint"][src]
        if orphans:
            self.save_store()
        return f"清理孤立文件{len(orphans)}个、残留片段{cleaned}段"
    
    # ---------------- 检索 ----------------
    @staticmethod
    def calc_similarity(v1: List[float], v2: List[float]) -> float:
        a, b = np.asarray(v1, np.float32), np.asarray(v2, np.float32)
        return float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) or 1.0))
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        docs = self.store.get("doc_list", [])
        if not docs:
            return []
        q = self.get_embedding(query)
        scored = [{
            "score": round(self.calc_similarity(q, d["vector"]), 4),
            "content": d["content"], "source": d["source"],
            "chunk_idx": d.get("chunk_idx", 0),
        } for d in docs]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
    
    def search_as_text(self, query: str, top_k: int = 3) -> str:
        hits = self.search(query, top_k)
        return "\n\n".join(
            f"[来源：{h['source']} 片段{h['chunk_idx']}]\n{h['content']}" for h in hits
        )
    
    # ---------------- 管理 ----------------
    def clear_kb(self) -> str:
        self.store = {"doc_list": [], "file_fingerprint": {}}
        self.save_store()
        return "知识库已清空"
    
    def stats(self) -> Dict[str, Any]:
        docs = self.store.get("doc_list", [])
        return {
            "documents": len(self.store.get("file_fingerprint", {})),
            "sources": sorted(self.store.get("file_fingerprint", {}).keys()),
            "chunks": len(docs),
            "embedding_dim": len(docs[0]["vector"]) if docs else 0,
        }


kb = LocalKnowledgeBase()
