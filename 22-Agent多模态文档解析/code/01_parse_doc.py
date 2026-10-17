# ===== parse_doc.py：PDF/Word/MD 解析 =====

import os
from PyPDF2 import PdfReader
from docx import Document

def parse_file_to_text(file_path: str) -> str:
    """
    通用文档解析器：支持 pdf / docx / txt / md
    统一返回纯文本内容
    """
    if not os.path.exists(file_path):
        return f"文件不存在：{file_path}"

    suffix = file_path.lower().split(".")[-1]
    content = ""

    try:
        if suffix in ["txt", "md"]:
            # 纯文本/马克down直接读取
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        elif suffix == "pdf":
            # PDF逐页解析
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    content += page_text + "\n"

        elif suffix == "docx":
            # Word文档逐段落解析
            doc = Document(file_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    content += para.text.strip() + "\n"

        else:
            return f"暂不支持解析该格式：.{suffix}"

    except Exception as e:
        return f"文档解析失败：{str(e)}"

    return content.strip()
