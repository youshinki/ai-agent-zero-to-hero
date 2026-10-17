# ===== kb_core.py：新增导入 =====

from .parse_doc import parse_file_to_text
from .text_cleaner import cleaner

# ===== 替换旧切片方法为智能清洗切片 =====

# 废弃原有粗暴切片
# def split_text(self, text):
#     chunks = []
#     start = 0
#     while start < len(text):
#         end = start + CHUNK_SIZE
#         chunk = text[start:end]
#         chunks.append(chunk)
#         start = end - CHUNK_OVERLAP
#     return chunks

# 新增智能清洗+语义切片
def split_text(self, text):
    # 1. 全文四级净化
    clean_text = cleaner.full_clean(text)
    # 2. 语义智能切片
    chunks = cleaner.smart_chunk_split(
        clean_text,
        chunk_size=CHUNK_SIZE,
        overlap=CHUNK_OVERLAP
    )
    return chunks
