#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第21篇配套 · test_incremental.py
验证增量更新全流程：
  1. 首次入库（全量）
  2. 再次扫描（无变动 → 跳过）
  3. 修改文件（检测到变动 → 增量更新）
  4. 新增文件（只处理新增）
  5. 删除文件（自动清理残留向量）

运行: python test_incremental.py
"""

import os
import time

from knowledge_base.kb_core import kb, get_file_md5

UPLOAD_DIR = "knowledge_base/upload_doc"


def write(name: str, content: str):
    path = os.path.join(UPLOAD_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def main():
    print("=" * 64)
    print("🧪 增量知识库自动更新测试")
    print("=" * 64)

    # 清理
    kb.clear_kb()
    for f in os.listdir(UPLOAD_DIR):
        if f.endswith((".txt", ".md")):
            os.remove(os.path.join(UPLOAD_DIR, f))

    # 1. 首次入库
    print("\n[1] 首次全量入库")
    write("a.txt", "AI Agent 是目标驱动的智能程序，具备规划、记忆、工具、反思能力。")
    write("b.txt", "RAG 通过检索私有资料增强生成，显著降低幻觉。")
    log = kb.scan_all_update()
    for x in log:
        print(f"   {x['message']}")
    print(f"   统计：{kb.stats()}")

    # 2. 无变动扫描
    print("\n[2] 无变动扫描（应全部跳过）")
    log = kb.scan_all_update()
    for x in log:
        print(f"   {x['status']} | {x['message']}")
    assert all(x["status"] == "unchanged" for x in log), "无变动时应跳过"

    # 3. 修改文件
    print("\n[3] 修改 a.txt（应增量更新）")
    time.sleep(0.01)
    write("a.txt", "AI Agent 是目标驱动的智能程序，具备规划、记忆、工具、反思、纠错能力。新增内容：支持多Agent协作。")
    log = kb.scan_all_update()
    for x in log:
        print(f"   {x['status']} | {x['message']}")
    updated = [x for x in log if x["status"] == "updated"]
    assert len(updated) == 1 and updated[0]["file"] == "a.txt", "应只更新a.txt"

    # 4. 新增文件
    print("\n[4] 新增 c.txt（应只处理新增）")
    write("c.txt", "工具调用让Agent从「会说」变成「会做」，可以读写文件、执行计算、调用API。")
    log = kb.scan_all_update()
    for x in log:
        print(f"   {x['status']} | {x['message']}")
    assert any(x["file"] == "c.txt" and x["status"] == "updated" for x in log)

    # 5. 删除文件
    print("\n[5] 删除 b.txt（应自动清理向量）")
    os.remove(os.path.join(UPLOAD_DIR, "b.txt"))
    msg = kb.cleanup_orphans()
    print(f"   {msg}")
    stats = kb.stats()
    print(f"   统计：{stats}")
    assert "b.txt" not in stats["sources"], "b.txt 残留未清理"

    # 6. 检索验证
    print("\n[6] 检索验证（内容已更新）")
    hits = kb.search("多Agent协作", top_k=2)
    for h in hits:
        print(f"   [{h['score']}] {h['source']}：{h['content'][:60]}...")

    # 7. 指纹验证
    print("\n[7] 文件指纹验证")
    fp_a = get_file_md5(os.path.join(UPLOAD_DIR, "a.txt"))
    print(f"   a.txt 指纹：{fp_a[:16]}...  库内指纹一致：{kb.store['file_fingerprint'].get('a.txt') == fp_a}")
    assert kb.store["file_fingerprint"].get("a.txt") == fp_a

    print("\n✅ 增量知识库测试全部通过")


if __name__ == "__main__":
    main()
