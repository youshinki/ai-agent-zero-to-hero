#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第74篇配套 · test_anti_hallucination.py
"""

from anti_hallucination import (
    EvidenceBase, CitationVerifier, ConflictDetector,
    FaithfulnessScorer, demo,
)


def main():
    print("=" * 66)
    print("🧪 RAG 幻觉根治测试")
    print("=" * 66)

    kb = EvidenceBase()
    kb.add("price.txt", "标准版定价19800元，支持20个用户。")
    kb.add("ops.txt", "部署需要4核CPU、16GB内存，备份每日凌晨2点。")
    kb.add("conflict.txt", "标准版定价15800元，支持15个用户。")

    print("\n[1] 检索：")
    ev = kb.search("标准版定价")
    assert ev and ev[0]["doc_id"] in ("price.txt", "conflict.txt")
    print(f"   命中：{[e['doc_id'] for e in ev]}")

    print("\n[2] 引用溯源（真实陈述）：")
    r = CitationVerifier.verify_statement("标准版定价19800元", ev)
    # 两个文档都有定价，可能冲突，但19800在price.txt中
    assert not r["unsupported_numbers"]
    print(f"   无据数字：{r['unsupported_numbers']}")

    print("\n[3] 伪造检测：")
    fake = "标准版定价99999元"
    r = CitationVerifier.verify_statement(fake, ev)
    assert "99999" in r["unsupported_numbers"]
    assert not r["supported"]
    print(f"   ✅ 检出伪造数字：{r['unsupported_numbers']}")

    print("\n[4] 冲突检测：")
    conflicts = ConflictDetector.detect(kb.docs)
    assert conflicts, "应检测到定价冲突"
    metrics = [c["metric"] for c in conflicts]
    print(f"   ✅ 冲突指标：{metrics[:3]}")

    print("\n[5] 忠实度：")
    good = FaithfulnessScorer.score("标准版定价19800元。支持20个用户。", ev)
    bad = FaithfulnessScorer.score("标准版定价99999元。赠送十年服务。", ev)
    assert good["score"] > bad["score"]
    print(f"   好：{good['score']}（{good['grade']}）｜坏：{bad['score']}（{bad['grade']}）")

    print("\n[6] 无据拒答：")
    ev_none = kb.search("股票代码")
    assert FaithfulnessScorer.should_refuse(ev_none)
    ev_ok = kb.search("定价")
    assert not FaithfulnessScorer.should_refuse(ev_ok)
    print("   ✅ 无证据拒答，有证据放行")

    print("\n[7] 演示：")
    demo()
    print("\n✅ 幻觉根治测试通过")


if __name__ == "__main__":
    main()
