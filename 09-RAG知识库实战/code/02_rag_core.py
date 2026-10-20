# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 rag_agent/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

from openai import OpenAI
import faiss
import numpy as np
import os
from config import *

client = OpenAI(
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL
)

class RAGCore:
    def __init__(self):
        self.chunks = []
        self.index = None

    # 1. 加载本地文档
    def load_doc(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return text

    # 2. 文本分块处理
    def split_chunk(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk = text[start:end]
            chunks.append(chunk)
            # 重叠切割，保证上下文连贯
            start = end - CHUNK_OVERLAP
        self.chunks = chunks
        return chunks

    # 3. 文本向量化
    def get_embedding(self, text):
        res = client.embeddings.create(
            input=text,
            model=EMBED_MODEL_NAME
        )
        return res.data[0].embedding

    # 4. 构建本地向量库
    def build_vector_store(self):
        embeddings = [self.get_embedding(chunk) for chunk in self.chunks]
        embeddings_np = np.array(embeddings).astype("float32")
        # 初始化FAISS索引
        self.index = faiss.IndexFlatL2(embeddings_np.shape[1])
        self.index.add(embeddings_np)

    # 5. 相似度检索
    def search_relevant(self, query):
        query_emb = np.array([self.get_embedding(query)]).astype("float32")
        distances, indices = self.index.search(query_emb, TOP_K)
        # 捞出最相关的文本块
        relevant_chunks = [self.chunks[i] for i in indices[0]]
        return "\n\n".join(relevant_chunks)

    # 初始化知识库
    def init_knowledge_base(self, doc_path):
        print("正在加载文档...")
        text = self.load_doc(doc_path)
        print("正在文本分块...")
        self.split_chunk(text)
        print("正在构建向量知识库...")
        self.build_vector_store()
        print("✅ 知识库初始化完成！")
