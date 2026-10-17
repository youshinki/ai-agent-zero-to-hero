from dotenv import load_dotenv
import os

load_dotenv()

# 大模型配置
MODEL_API_KEY = os.getenv("API_KEY")
MODEL_BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = "deepseek-chat"

# Embedding嵌入模型配置（通用兼容）
EMBED_MODEL_NAME = "text-embedding-ada-002"

# RAG参数设置
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
TOP_K = 3
