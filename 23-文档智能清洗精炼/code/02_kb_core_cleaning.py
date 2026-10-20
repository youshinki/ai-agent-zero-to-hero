# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 agent_clean_kb/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

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
