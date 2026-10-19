#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第22篇配套完整项目代码 · knowledge_base/parse_doc.py
通用文档解析器：pdf / docx / txt / md → 统一纯文本

解析策略（文章第二章）：
  1. 格式识别：判断后缀
  2. 分区解析：各格式调用对应解析器
  3. 内容统一：输出标准纯文本
  4. 复用旧流程：交给切片/向量化/增量入库

实现说明：
  - txt/md：直接读取
  - docx：使用 Python 内置 zipfile + xml 解析（零依赖）
  - pdf ：优先 PyPDF2 / pypdf（可选安装）
==========================================================================
"""

import os
import re
import zipfile
from xml.etree import ElementTree as ET


def parse_file_to_text(file_path: str) -> str:
    """通用文档解析器：支持 pdf / docx / txt / md，统一返回纯文本"""
    if not os.path.exists(file_path):
        return f"文件不存在：{file_path}"
    
    suffix = file_path.lower().rsplit(".", 1)[-1] if "." in file_path else ""
    
    try:
        if suffix in ("txt", "md"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        
        if suffix == "docx":
            return _parse_docx(file_path)
        
        if suffix == "pdf":
            return _parse_pdf(file_path)
        
        return f"暂不支持解析该格式：.{suffix}"
    
    except Exception as e:
        return f"文档解析失败：{e}"


def _parse_docx(file_path: str) -> str:
    """解析 DOCX（零依赖：docx 本质是 zip，正文在 word/document.xml）"""
    try:
        with zipfile.ZipFile(file_path) as z:
            xml_bytes = z.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile):
        # 兜底：尝试 python-docx（若已安装）
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
        except ImportError:
            return "文档解析失败：无效的 DOCX 文件"
    
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    root = ET.fromstring(xml_bytes)
    lines = []
    for para in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        texts = [t.text for t in para.iter(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if t.text]
        line = "".join(texts).strip()
        if line:
            lines.append(line)
    return "\n".join(lines).strip() or "（DOCX 无文本内容）"


def _parse_pdf(file_path: str) -> str:
    """解析 PDF（优先 PyPDF2，其次 pypdf）"""
    reader = None
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
    except ImportError:
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
        except ImportError:
            return ("文档解析失败：缺少PDF解析库。请安装：pip install PyPDF2"
                    "（或 pip install pypdf）")
    
    content = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            content.append(text)
    return "\n".join(content).strip() or "（PDF 无可用文本，可能是扫描件）"


if __name__ == "__main__":
    # 快速自测
    import sys
    if len(sys.argv) > 1:
        print(parse_file_to_text(sys.argv[1])[:500])
    else:
        print("用法: python parse_doc.py <文件路径>")
