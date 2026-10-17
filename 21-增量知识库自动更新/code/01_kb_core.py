# ===== kb_core.py：增量更新+MD5指纹 =====

import json
import os
import hashlib
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

# 文本切片参数
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

def get_file_md5(file_path):
    """获取文件MD5指纹，用于监测文件变动"""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()

class LocalKnowledgeBase:
    def __init__(self):
        self.store = self.load_store()

    def load_store(self):
        """加载本地向量数据库，兼容旧版本"""
        if os.path.exists(KB_STORE_PATH):
            with open(KB_STORE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 兼容旧数据，新增指纹字典
            if "file_fingerprint" not in data:
                data["file_fingerprint"] = {}
            if "doc_list" not in data:
                data["doc_list"] = []
            return data
        return {"doc_list": [], "file_fingerprint": {}}

    def save_store(self):
        """保存知识库数据"""
        with open(KB_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.store, f, ensure_ascii=False, indent=2)

    def split_text(self, text):
        """长文本切片"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - CHUNK_OVERLAP
        return chunks

    def get_embedding(self, text):
        """生成向量嵌入"""
        res = client.embeddings.create(
            model=EMBED_MODEL_NAME,
            input=text
        )
        return res.data[0].embedding

    def single_file_increment_update(self, file_path):
        """单文件增量更新核心逻辑"""
        if not os.path.exists(file_path):
            # 文件已删除，清理该文件所有向量
            return self.clean_file_vector(os.path.basename(file_path))

        file_name = os.path.basename(file_path)
        new_md5 = get_file_md5(file_path)

        # 1. 文件未改动，直接跳过
        if file_name in self.store["file_fingerprint"]:
            old_md5 = self.store["file_fingerprint"][file_name]
            if new_md5 == old_md5:
                return f"【无需更新】文件无变动：{file_name}"

        # 2. 文件已修改，先清理旧向量
        self.clean_file_vector(file_name)

        # 3. 重新切片、向量化、增量入库
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        chunks = self.split_text(content)

        for idx, chunk in enumerate(chunks):
            vec = self.get_embedding(chunk)
            self.store["doc_list"].append({
                "source": file_name,
                "chunk_idx": idx,
                "content": chunk,
                "vector": vec
            })

        # 4. 更新文件指纹
        self.store["file_fingerprint"][file_name] = new_md5
        self.save_store()
        return f"【增量更新成功】{file_name}，新增切片{len(chunks)}段"

    def clean_file_vector(self, file_name):
        """清理指定文件所有旧向量数据"""
        old_count = len(self.store["doc_list"])
        # 过滤掉该文件所有旧片段
        self.store["doc_list"] = [
            item for item in self.store["doc_list"]
            if item["source"] != file_name
        ]
        # 清除指纹
        if file_name in self.store["file_fingerprint"]:
            del self.store["file_fingerprint"][file_name]
        self.save_store()
        return f"清理旧向量片段{old_count - len(self.store['doc_list'])}段"

    def scan_all_update(self):
        """扫描全部文档，全自动增量更新"""
        update_log = []
        # 遍历upload_doc下所有txt/md文件
        for fname in os.listdir(UPLOAD_DOC_PATH):
            if fname.endswith((".txt", ".md")):
                fpath = os.path.join(UPLOAD_DOC_PATH, fname)
                res = self.single_file_increment_update(fpath)
                update_log.append(res)
        return update_log

    def calc_similarity(self, vec1, vec2):
        """余弦相似度计算"""
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)
        return np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))

    def search(self, query, top_k=3):
        """语义检索"""
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

        score_list = sorted(score_list, key=lambda x: x["score"], reverse=True)
        return score_list[:top_k]

    def clear_kb(self):
        """清空全量知识库"""
        self.store = {"doc_list": [], "file_fingerprint": {}}
        self.save_store()
        return "全量知识库已清空"

# 全局单例
kb = LocalKnowledgeBase()
