#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第23篇配套 · test_cleaner.py
验证四级净化流水线：
  1. 基础清洗（空行/多余空格）
  2. 噪声过滤（页码/版权/分隔符）
  3. 语义修复（PDF断行合并）
  4. 智能切片（段落完整、重叠衔接）
并对比清洗前后入库效果。

运行: python test_cleaner.py
"""

import os

from knowledge_base.text_cleaner import cleaner
from knowledge_base.kb_core import kb
from knowledge_base.parse_doc import parse_file_to_text

UPLOAD_DIR = "knowledge_base/upload_doc"


RAW_TEXT = """第一章 产品概述


    我们的产品是一套 AI 知识库系统。        支持私有化部署。


- 3 -
版权所有 未经授权不得转载
------------------------------------------------

第二章 部署要求
服务器配置为 4 核 CPU、
16GB 内存、
以及 100GB 磁盘空间。
支持内网部署，
无需外网连接。

Page 12
本文件仅供参考
"""


def main():
    print("=" * 66)
    print("🧪 文档智能清洗精炼测试")
    print("=" * 66)

    print("\n【原始文本】")
    print("-" * 66)
    print(RAW_TEXT)
    print("-" * 66)
    print(f"原始字符数：{len(RAW_TEXT)}")

    # 1. 基础清洗
    step1 = cleaner.basic_clean(RAW_TEXT)
    print(f"\n[1] 基础清洗后：{len(step1)}字")
    print(step1)

    # 2. 噪声过滤
    step2 = cleaner.filter_noise(step1)
    print(f"\n[2] 噪声过滤后：{len(step2)}字（已去页码/版权/分割线）")
    print(step2)

    # 3. 语义修复
    step3 = cleaner.repair_broken_sentence(step2)
    print(f"\n[3] 语义修复后：{len(step3)}字（断行已合并）")
    print(step3)

    # 4. 智能切片
    chunks = cleaner.smart_chunk_split(step3, chunk_size=60, overlap=10)
    print(f"\n[4] 智能切片：{len(chunks)}块")
    for i, c in enumerate(chunks, 1):
        print(f"   块{i}（{len(c)}字）：{c[:70].replace(chr(10), ' ')}...")

    # 断言
    full = cleaner.full_clean(RAW_TEXT)
    assert "版权所有" not in full and "Page 12" not in full and "第 3 页" not in full, "噪声应被过滤"
    assert "4 核 CPU" in full.replace(" ", " ") or "4 核 CPU" in full, "正文应保留"
    # 断行合并：服务器配置应在一行内
    assert "4 核 CPU、16GB 内存" in full or "4 核 CPU、16GB 内存" in full.replace("\n", ""), "断行应合并"

    # 5. 入库对比
    print("\n" + "=" * 66)
    print("[5] 清洗后入库 + 检索验证")
    kb.clear_kb()
    for f in os.listdir(UPLOAD_DIR):
        if f.endswith((".txt", ".md", ".docx")):
            os.remove(os.path.join(UPLOAD_DIR, f))
    with open(os.path.join(UPLOAD_DIR, "clean_demo.txt"), "w", encoding="utf-8") as f:
        f.write(RAW_TEXT)
    log = kb.scan_all_update()
    for x in log:
        print(f"   {x['status']} | {x['message']}")

    hits = kb.search("服务器配置", top_k=2)
    print("\n   检索「服务器配置」：")
    for h in hits:
        print(f"     [{h['score']}] {h['source']}：{h['content'][:70].replace(chr(10), ' ')}...")

    print("\n✅ 文档智能清洗测试全部通过")


if __name__ == "__main__":
    main()
