# ===== knowledge_base/kb_core.py：切片/向量化/检索 =====

import json
import os
import numpy as np
from openai import OpenAI
from config import MODEL_API_KEY, MODEL_BASE_URL, EMBED_MODEL_NAME

# 初始化向量模型客户端
client = OpenAI(
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL
)

# 知识库路径配置
KB_DIR = "knowledge_base"
KB_STORE_PATH = os.path.join(KB_DIR, "kb_store.json")
UPLOAD_DOC_PATH = os.path.join(KB_DIR, "upload_doc")

# 确保目录存在
os.makedirs(KB_DIR, exist_ok=True)
os.makedirs(UPLOAD_DOC_PATH, exist_ok=True)

# 文本切片大小
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

class LocalKnowledgeBase:
    def __init__(self):
        # 初始化向量库
        self.store = self.load_store()

    def load_store(self):
        """加载本地向量数据库"""
        if os.path.exists(KB_STORE_PATH):
            with open(KB_STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"doc_list": []}

    def save_store(self):
        """保存向量数据库到本地"""
        with open(KB_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.store, f, ensure_ascii=False, indent=2)

    def split_text(self, text):
        """长文本智能切片"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - CHUNK_OVERLAP
        return chunks

    def get_embedding(self, text):
        """生成文本向量"""
        res = client.embeddings.create(
            model=EMBED_MODEL_NAME,
            input=text
        )
        return res.data[0].embedding

    def add_doc_file(self, file_path):
        """读取文档、切片、向量化、入库"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"文档读取失败：{str(e)}"

        # 文本切片
        chunks = self.split_text(content)
        # 批量向量化入库
        for idx, chunk in enumerate(chunks):
            vec = self.get_embedding(chunk)
            self.store["doc_list"].append({
                "source": os.path.basename(file_path),
                "chunk_idx": idx,
                "content": chunk,
                "vector": vec
            })
        self.save_store()
        return f"文档入库成功！共切片 {len(chunks)} 段内容"

    def calc_similarity(self, vec1, vec2):
        """余弦相似度计算"""
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)
        return np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))

    def search(self, query, top_k=3):
        """语义检索，返回最匹配的内容"""
        if not self.store["doc_list"]:
            return "知识库暂无任何私有文档内容"

        query_vec = self.get_embedding(query)
        score_list = []

        for item in self.store["doc_list"]:
            score = self.calc_similarity(query_vec, item["vector"])
            score_list.append({
                "score": score,
                "content": item["content"],
                "source": item["source"]
            })

        # 相似度倒序排序
        score_list = sorted(score_list, key=lambda x: x["score"], reverse=True)
        return score_list[:top_k]

    def clear_kb(self):
        """清空知识库"""
        self.store = {"doc_list": []}
        self.save_store()
        return "知识库已清空"

# 全局单例
kb = LocalKnowledgeBase()

# ===== config.py：向量嵌入模型配置 =====

# 向量嵌入模型配置（写入 .env 或 config.py，供 kb_core.py 导入）
# EMBED_MODEL_NAME = "text-embedding-ada-002"
