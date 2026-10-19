#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第74篇配套完整项目代码 · anti_hallucination.py
RAG 幻觉深度根治：事实校验、引用溯源、冲突文档自动检测

  1. 引用溯源（每个陈述绑定来源）
  2. 事实校验（数字/实体核对）
  3. 冲突检测（多文档矛盾）
  4. 忠实度评分
  5. 无据拒答
==========================================================================
"""

import re
from typing import Dict, List, Optional


# ======================================================================
# 一、文档库
# ======================================================================

class EvidenceBase:
    def __init__(self):
        self.docs: Dict[str, str] = {}
    
    def add(self, doc_id: str, content: str):
        self.docs[doc_id] = content
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        scored = []
        for doc_id, content in self.docs.items():
            score = len(set(query) & set(content)) / max(len(set(query)), 1)
            scored.append({"doc_id": doc_id, "content": content,
                           "score": round(score, 3)})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return [s for s in scored[:top_k] if s["score"] > 0.1]


# ======================================================================
# 二、引用溯源
# ======================================================================

class CitationVerifier:
    @staticmethod
    def extract_numbers(text: str) -> List[str]:
        return re.findall(r"\d+(?:\.\d+)?%?", text)
    
    @staticmethod
    def verify_statement(statement: str, evidence: List[Dict]) -> Dict:
        """检查陈述中的关键信息是否有来源支撑"""
        nums = CitationVerifier.extract_numbers(statement)
        evidence_text = " ".join(e["content"] for e in evidence)
        
        unsupported = [n for n in nums if n not in evidence_text]
        # 实体（中文词块）覆盖
        entities = re.findall(r"[\u4e00-\u9fa5]{2,6}", statement)
        covered = [e for e in entities if e in evidence_text]
        coverage = len(covered) / len(entities) if entities else 1.0
        
        supported = (not unsupported) and coverage >= 0.5
        return {
            "statement": statement[:50],
            "supported": supported,
            "unsupported_numbers": unsupported,
            "entity_coverage": round(coverage, 2),
            "sources": [e["doc_id"] for e in evidence if
                        any(n in e["content"] for n in nums)] or
                       [e["doc_id"] for e in evidence[:1]],
        }


# ======================================================================
# 三、冲突检测
# ======================================================================

class ConflictDetector:
    @staticmethod
    def detect(docs: Dict[str, str]) -> List[Dict]:
        """检测文档中同一指标的不同数值"""
        conflicts = []
        # 提取"指标 = 数值"模式
        claims: Dict[str, List[Dict]] = {}
        for doc_id, content in docs.items():
            for m in re.finditer(
                    r"([\u4e00-\u9fa5]{2,8})(?:为|是|达到|约)?\s*(\d+(?:\.\d+)?%?)\s*(元|万元|%|个|天)?",
                    content):
                key, value = m.group(1), m.group(2) + (m.group(3) or "")
                claims.setdefault(key, []).append(
                    {"doc": doc_id, "value": value})
        
        for key, items in claims.items():
            values = {i["value"] for i in items}
            if len(values) > 1 and len(items) >= 2:
                conflicts.append({"metric": key, "values": list(values),
                                  "sources": items})
        return conflicts


# ======================================================================
# 四、忠实度评分与拒答
# ======================================================================

class FaithfulnessScorer:
    @staticmethod
    def score(answer: str, evidence: List[Dict]) -> Dict:
        sentences = [s for s in re.split(r"[。；！？]", answer) if s.strip()]
        if not sentences:
            return {"score": 0, "details": []}
        
        ev_text = " ".join(e["content"] for e in evidence)
        supported = 0
        details = []
        for s in sentences:
            # 句子中2字词在证据中的比例
            words = re.findall(r"[\u4e00-\u9fa5]{2,4}", s)
            if not words:
                continue
            hit = sum(1 for w in words if w in ev_text) / len(words)
            ok = hit >= 0.5
            supported += 1 if ok else 0
            details.append({"sentence": s[:30], "overlap": round(hit, 2),
                            "supported": ok})
        
        rate = supported / len(sentences) if sentences else 0
        return {"score": round(rate * 100, 1),
                "grade": "高" if rate >= 0.8 else ("中" if rate >= 0.5 else "低"),
                "details": details}
    
    @staticmethod
    def should_refuse(evidence: List[Dict], min_score: float = 0.2) -> bool:
        return (not evidence) or (evidence[0]["score"] < min_score)


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("🎯 RAG 幻觉深度根治演示")
    print("=" * 66)
    
    kb = EvidenceBase()
    kb.add("price.txt", "标准版定价19800元，支持20个用户。基础版9800元。")
    kb.add("ops.txt", "部署需要4核CPU、16GB内存，数据备份每日凌晨2点执行。")
    kb.add("conflict.txt", "标准版定价15800元，支持15个用户。")
    
    print("\n[1] 引用溯源：")
    ev = kb.search("标准版定价多少")
    ans = "标准版定价19800元，支持20个用户。"
    r = CitationVerifier.verify_statement(ans, ev)
    print(f"   陈述：{ans}")
    print(f"   有据可查：{r['supported']}，来源：{r['sources']}")
    
    print("\n[2] 伪造数字检测：")
    fake = "标准版定价12800元，支持50个用户。"
    r = CitationVerifier.verify_statement(fake, ev)
    print(f"   陈述：{fake}")
    print(f"   无据数字：{r['unsupported_numbers']}，有据：{r['supported']}")
    
    print("\n[3] 冲突检测：")
    conflicts = ConflictDetector.detect(kb.docs)
    for c in conflicts[:2]:
        print(f"   ⚠️ {c['metric']} 存在冲突：{c['values']}")
    
    print("\n[4] 忠实度：")
    good = "标准版定价19800元。支持20个用户。"
    bad = "标准版定价12800元。支持50个用户。赠送3年服务。"
    print(f"   好答案：{FaithfulnessScorer.score(good, ev)['score']}分")
    print(f"   坏答案：{FaithfulnessScorer.score(bad, ev)['score']}分")
    
    print("\n[5] 无据拒答：")
    ev2 = kb.search("股票代码")
    print(f"   无相关证据 → 拒答：{FaithfulnessScorer.should_refuse(ev2)}")


if __name__ == "__main__":
    demo()
