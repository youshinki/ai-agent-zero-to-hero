# ===== kb_core.py：重排序+融合检索完整版 =====

import json
import os
import hashlib
import numpy as np
from openai import OpenAI
from config import MODEL_API_KEY, MODEL_BASE_URL, EMBED_MODEL_NAME
from .parse_doc import parse_file_to_text
from .text_cleaner import cleaner

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

# 检索超参（商用最优配置）
INIT_RECALL_TOPK = 10   # 初始多路扩召数量
FINAL_TOPK = 3          # 最终留存片段数量
SIMILARITY_WEIGHT = 0.7 # 语义相似度权重
KEYWORD_WEIGHT = 0.3    # 关键词匹配权重

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
        """智能清洗+语义切片（历史最优能力保留）"""
        clean_text = cleaner.full_clean(text)
        chunks = cleaner.smart_chunk_split(
            clean_text,
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP
        )
        return chunks

    def get_embedding(self, text):
        """生成向量嵌入"""
        res = client.embeddings.create(
            model=EMBED_MODEL_NAME,
            input=text
        )
        return res.data[0].embedding

    def single_file_increment_update(self, file_path):
        """单文件增量更新核心逻辑（完全保留）"""
        if not os.path.exists(file_path):
            return self.clean_file_vector(os.path.basename(file_path))

        file_name = os.path.basename(file_path)
        new_md5 = get_file_md5(file_path)

        if file_name in self.store["file_fingerprint"]:
            old_md5 = self.store["file_fingerprint"][file_name]
            if new_md5 == old_md5:
                return f"【无需更新】文件无变动：{file_name}"

        self.clean_file_vector(file_name)
        content = parse_file_to_text(file_path)

        if content.startswith("文档解析失败") or content.startswith("暂不支持解析"):
            return f"【解析失败】{file_name}：{content}"

        chunks = self.split_text(content)
        for idx, chunk in enumerate(chunks):
            vec = self.get_embedding(chunk)
            self.store["doc_list"].append({
                "source": file_name,
                "chunk_idx": idx,
                "content": chunk,
                "vector": vec
            })

        self.store["file_fingerprint"][file_name] = new_md5
        self.save_store()
        return f"【增量更新成功】{file_name}，新增切片{len(chunks)}段"

    def clean_file_vector(self, file_name):
        """清理指定文件所有旧向量数据"""
        old_count = len(self.store["doc_list"])
        self.store["doc_list"] = [
            item for item in self.store["doc_list"]
            if item["source"] != file_name
        ]
        if file_name in self.store["file_fingerprint"]:
            del self.store["file_fingerprint"][file_name]
        self.save_store()
        return f"清理旧向量片段{old_count - len(self.store['doc_list'])}段"

    def scan_all_update(self):
        """扫描全部文档，全自动增量更新"""
        update_log = []
        for fname in os.listdir(UPLOAD_DOC_PATH):
            if fname.endswith((".txt", ".md", ".pdf", ".docx")):
                fpath = os.path.join(UPLOAD_DOC_PATH, fname)
                res = self.single_file_increment_update(fpath)
                update_log.append(res)
        return update_log

    def calc_similarity(self, vec1, vec2):
        """余弦相似度计算"""
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)
        return np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))

    def calc_keyword_score(self, query, content):
        """计算关键词匹配得分，弥补向量语义盲区"""
        query_words = set(query.strip().split())
        content_words = set(content.strip().split())
        if not query_words:
            return 0.0
        match_num = len(query_words & content_words)
        return match_num / len(query_words)

    def rerank_results(self, query, raw_results):
        """
        核心：多路结果智能重排序
        融合语义相似度 + 关键词匹配双重权重
        """
        rerank_list = []
        for item in raw_results:
            sim_score = item["score"]
            keyword_score = self.calc_keyword_score(query, item["content"])
            # 加权综合得分
            total_score = sim_score * SIMILARITY_WEIGHT + keyword_score * KEYWORD_WEIGHT
            rerank_list.append({
                "total_score": round(total_score, 4),
                "sim_score": sim_score,
                "keyword_score": keyword_score,
                "content": item["content"],
                "source": item["source"]
            })
        # 综合得分倒序排序
        return sorted(rerank_list, key=lambda x: x["total_score"], reverse=True)

    def fuse_dup_content(self, sorted_results):
        """
        高分片段去重融合
        剔除高度冗余内容，保留差异化有效信息
        """
        if not sorted_results:
            return []
        
        fuse_list = []
        exist_contents = []

        for item in sorted_results:
            current_content = item["content"]
            # 判断是否高度重复（简单相似度匹配）
            is_dup = False
            for exist in exist_contents:
                # 内容重叠度超过60%判定为冗余
                overlap_len = len(set(current_content) & set(exist))
                if overlap_len / len(set(current_content)) > 0.6:
                    is_dup = True
                    break
            if not is_dup:
                fuse_list.append(item)
                exist_contents.append(current_content)
        
        # 截取最终最优TopN
        return fuse_list[:FINAL_TOPK]

    def search(self, query):
        """
        全新高精度检索入口：多路扩召 -> 重排序 -> 去重融合
        """
        if not self.store["doc_list"]:
            return "知识库暂无任何私有文档内容"

        # 1. 多路扩召：先召回更多候选片段，杜绝漏召
        query_vec = self.get_embedding(query)
        raw_score_list = []

        for item in self.store["doc_list"]:
            sim_score = self.calc_similarity(query_vec, item["vector"])
            raw_score_list.append({
                "score": sim_score,
                "content": item["content"],
                "source": item["source"]
            })

        # 初始召回排序
        raw_top = sorted(raw_score_list, key=lambda x: x["score"], reverse=True)[:INIT_RECALL_TOPK]
        # 2. 智能权重重排序
        rerank_top = self.rerank_results(query, raw_top)
        # 3. 去重融合、筛选最优片段
        final_results = self.fuse_dup_content(rerank_top)

        # 格式化输出最终检索内容
        if not final_results:
            return "未检索到相关私有文档内容"
        
        out = "【高精度知识库检索结果】\n"
        for idx, item in enumerate(final_results):
            out += f"\n片段{idx+1}（综合匹配分：{item['total_score']}）\n"
            out += f"来源文档：{item['source']}\n"
            out += f"核心内容：{item['content']}\n"
        return out

    def clear_kb(self):
        """清空全量知识库"""
        self.store = {"doc_list": [], "file_fingerprint": {}}
        self.save_store()
        return "全量知识库已清空"

# 全局单例
kb = LocalKnowledgeBase()
