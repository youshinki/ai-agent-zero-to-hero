#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第22篇配套 · test_multimodal.py
验证多模态文档解析 + 全格式批量入库：
  1. 创建一个真实的 DOCX（用 zipfile 生成，无需 python-docx）
  2. 入库 txt / md / docx 三种格式
  3. PDF 缺失解析库时优雅降级
  4. 全格式语义检索

运行: python test_multimodal.py
"""

import os
import zipfile
from xml.sax.saxutils import escape

from knowledge_base.kb_core import kb
from knowledge_base.parse_doc import parse_file_to_text

UPLOAD_DIR = "knowledge_base/upload_doc"


def create_docx(path: str, paragraphs):
    """用 zipfile 生成最小可用 DOCX（零依赖）"""
    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        + "".join(
            f"<w:p><w:r><w:t xml:space=\"preserve\">{escape(p)}</w:t></w:r></w:p>"
            for p in paragraphs
        )
        + "</w:body></w:document>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        "</Relationships>"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc_xml)


def main():
    print("=" * 64)
    print("🧪 多模态文档解析测试")
    print("=" * 64)

    kb.clear_kb()
    for f in os.listdir(UPLOAD_DIR):
        if f.endswith((".txt", ".md", ".docx", ".pdf")):
            os.remove(os.path.join(UPLOAD_DIR, f))

    # 1. 准备三种格式的文档
    print("\n[1] 准备测试文档")
    with open(os.path.join(UPLOAD_DIR, "notes.txt"), "w", encoding="utf-8") as f:
        f.write("TXT文档：AI Agent的核心能力包括规划、记忆、工具调用和反思纠错。")
    with open(os.path.join(UPLOAD_DIR, "guide.md"), "w", encoding="utf-8") as f:
        f.write("# Markdown文档\n\n.md 文件同样支持解析。RAG通过私有资料增强生成。")
    create_docx(os.path.join(UPLOAD_DIR, "manual.docx"), [
        "Word文档：产品部署手册",
        "服务器要求：4核CPU、16GB内存。",
        "部署方式：支持内网私有化部署。",
        "售后：交付后7天免费维护。",
    ])
    print("   已生成 notes.txt / guide.md / manual.docx")

    # 2. 单文件解析验证
    print("\n[2] 单文件解析验证：")
    for name in ["notes.txt", "guide.md", "manual.docx"]:
        text = parse_file_to_text(os.path.join(UPLOAD_DIR, name))
        print(f"   {name} → {len(text)}字 | {text[:50].replace(chr(10), ' ')}...")

    docx_text = parse_file_to_text(os.path.join(UPLOAD_DIR, "manual.docx"))
    assert "Word文档" in docx_text and "16GB内存" in docx_text, "DOCX解析应提取正文"

    # 3. 全格式批量入库
    print("\n[3] 全格式批量入库：")
    log = kb.scan_all_update()
    for x in log:
        print(f"   {x['status']} | {x['message']}")
    stats = kb.stats()
    print(f"   统计：{stats}")
    assert "manual.docx" in stats["sources"], "DOCX应入库"

    # 4. PDF 优雅降级
    print("\n[4] PDF 降级验证（未安装解析库时）")
    fake_pdf = os.path.join(UPLOAD_DIR, "sample.pdf")
    with open(fake_pdf, "wb") as f:
        f.write(b"%PDF-1.4\n%fake pdf content\n%%EOF")
    pdf_text = parse_file_to_text(fake_pdf)
    if pdf_text.startswith("文档解析失败"):
        print(f"   ✅ 优雅降级：{pdf_text}")
    else:
        print(f"   ℹ️ 已安装PDF库，解析结果：{pdf_text[:50]}")
    os.remove(fake_pdf)

    # 5. 跨格式语义检索
    print("\n[5] 跨格式语义检索：")
    for q in ["服务器配置要求", "私有化部署", "核心能力有哪些"]:
        hits = kb.search(q, top_k=2)
        print(f"\n   问：{q}")
        for h in hits:
            print(f"     [{h['score']}] {h['source']}：{h['content'][:50]}...")

    print("\n✅ 多模态文档解析测试完成")


if __name__ == "__main__":
    main()
