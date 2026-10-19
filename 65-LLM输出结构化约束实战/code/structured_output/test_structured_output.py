#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第65篇配套 · test_structured_output.py
"""

from structured_output import (
    ANSWER_SCHEMA, extract_json, repair_json, parse_robust,
    SchemaValidator, build_constrained_prompt, demo,
)


def main():
    print("=" * 66)
    print("🧪 结构化输出约束测试")
    print("=" * 66)

    print("\n[1] JSON 提取：")
    assert extract_json('前言 {"a": 1} 后记') == '{"a": 1}'
    assert extract_json("无json") is None
    assert extract_json('```json\n{"a": 1}\n```') == '{"a": 1}'
    assert extract_json('{"a": {"b": 2}}') == '{"a": {"b": 2}}'
    print("   ✅ 混合文本/代码块/嵌套/无JSON")

    print("\n[2] 修复：")
    fixed = repair_json("{'a': 1,}")
    assert '"a"' in fixed and not fixed.endswith(",")
    print(f"   {fixed}")

    print("\n[3] 鲁棒解析：")
    r = parse_robust('{"intent": "售前", "confidence": 0.9}')
    assert r["ok"] and not r["repaired"]
    r = parse_robust("{'intent': '售后', 'confidence': 0.8,}")
    assert r["ok"] and r["repaired"]
    r = parse_robust("抱歉不知道")
    assert not r["ok"]
    r = parse_robust('{"intent": "售前", "confidence": 0.')
    assert not r["ok"]  # 真截断无法修复
    print("   ✅ 标准/修复/无JSON/截断")

    print("\n[4] Schema 校验：")
    v = SchemaValidator()
    assert v.validate({"intent": "售前", "confidence": 0.9}, ANSWER_SCHEMA)["valid"]
    bad = v.validate({"intent": "未知", "confidence": 1.5}, ANSWER_SCHEMA)
    assert not bad["valid"] and len(bad["errors"]) >= 2
    missing = v.validate({"intent": "售前"}, ANSWER_SCHEMA)
    assert any("缺少" in e for e in missing["errors"])
    print(f"   ✅ 合法/枚举/范围/必填")

    print("\n[5] 约束Prompt：")
    p = build_constrained_prompt("判断意图", ANSWER_SCHEMA)
    assert "Schema" in p and "只输出 JSON" in p
    print("   ✅ 约束提示词完整")

    print("\n[6] 演示：")
    demo()
    print("\n✅ 结构化输出测试通过")


if __name__ == "__main__":
    main()
