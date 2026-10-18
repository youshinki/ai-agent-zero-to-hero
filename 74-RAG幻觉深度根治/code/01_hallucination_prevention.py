# 第74篇配套代码：RAG幻觉深度根治
# 事实校验、引用溯源、冲突文档自动检测
# 运行：python 01_hallucination_prevention.py

import json
from typing import List, Dict

# ========== 引用溯源Prompt ==========
CITATION_PROMPT = """根据下面【资料】回答用户问题。硬性规则：
1. 只能使用资料里明确出现的信息，不许补充资料外的内容。
2. 每个事实后面用 [^编号] 标注来源资料的编号。
3. 如果资料里没有答案，直接说"知识库中暂无相关信息"，不要编造。

【资料】
[1] {doc1}
[2] {doc2}
[3] {doc3}

问题：{query}
"""

# ========== 引用溯源系统 ==========
class CitationSystem:
    """引用溯源系统"""
    
    def __init__(self):
        self.documents = {}
    
    def add_document(self, doc_id, content, source=""):
        """添加文档"""
        self.documents[doc_id] = {
            "content": content,
            "source": source,
            "added_at": __import__("datetime").datetime.now().isoformat()
        }
    
    def verify_citation(self, statement, min_confidence=0.7):
        """验证单个陈述是否有据可查"""
        for doc_id, doc in self.documents.items():
            # 检查是否能找到支持依据
            overlap = len(set(statement) & set(doc["content"])) / max(len(set(statement)), 1)
            if overlap > min_confidence:
                return {
                    "verified": True,
                    "source": doc_id,
                    "confidence": overlap,
                    "document": doc["content"][:100]
                }
        
        return {
            "verified": False,
            "confidence": 0,
            "suggestion": "该陈述在知识库中找不到足够依据"
        }

# ========== 幻觉检测器 ==========
class HallucinationDetector:
    """幻觉检测"""
    
    @staticmethod
    def check_factual_consistency(statement, reference_docs):
        """检查事实一致性"""
        # 提取陈述中的关键事实
        facts = []
        sentences = statement.split("。")
        for sentence in sentences:
            if any(keyword in sentence for keyword in ["是", "有", "为", "包含", "属于"]):
                facts.append(sentence)
        
        issues = []
        for fact in facts:
            found_support = False
            for doc in reference_docs:
                # 检查关键实体是否在参考文档中
                entities = [word for word in fact.split() if len(word) > 1]
                matches = sum(1 for e in entities if e in doc)
                if matches >= 2:  # 至少2个实体匹配
                    found_support = True
                    break
            
            if not found_support:
                issues.append(f"可能幻觉：'{fact[:50]}...' 在知识库中无依据")
        
        return {
            "has_hallucination": len(issues) > 0,
            "issues": issues,
            "confidence": 1 - (len(issues) / max(len(facts), 1))
        }
    
    @staticmethod
    def cross_validate(answer, documents):
        """交叉验证答案"""
        doc_text = "\n".join(documents)
        
        # 提取数字和关键数据
        import re
        numbers_ans = set(re.findall(r'\d+\.?\d*', answer))
        numbers_doc = set(re.findall(r'\d+\.?\d*', doc_text))
        
        # 检查答案中的数字是否都在文档中
        unmatched_numbers = numbers_ans - numbers_doc
        if unmatched_numbers and len(unmatched_numbers) < len(numbers_ans):
            return {
                "valid": False,
                "unmatched_numbers": list(unmatched_numbers)[:5],
                "issue": f"发现{len(unmatched_numbers)}个无法溯源的数据"
            }
        
        return {"valid": True}

# ========== 冲突检测 ==========
class ConflictDetector:
    """文档冲突检测"""
    
    @staticmethod
    def detect_conflicts(documents):
        """检测文档间的冲突"""
        conflicts = []
        
        docs_list = list(documents.items())
        for i in range(len(docs_list)):
            for j in range(i+1, len(docs_list)):
                id1, doc1 = docs_list[i]
                id2, doc2 = docs_list[j]
                
                # 对比数值信息
                import re
                nums1 = set(re.findall(r'\d+\s*亿?元?', doc1["content"]))
                nums2 = set(re.findall(r'\d+\s*亿?元?', doc2["content"]))
                
                # 检查矛盾
                for n1 in nums1:
                    for n2 in nums2:
                        if n1.split()[0] == n2.split()[0] and n1 != n2:
                            conflicts.append({
                                "between": [id1, id2],
                                "conflict": f"'{n1}' vs '{n2}'",
                                "severity": "high"
                            })
        
        return conflicts

# ========== 生成质量评分 ==========
class QualityScorer:
    """生成质量评分"""
    
    @staticmethod
    def score_response(answer, sources):
        """评分回答质量"""
        score = 0
        details = []
        
        # 引用完整性
        citation_count = answer.count("[^")
        if citation_count >= 3:
            score += 3
            details.append("✅ 引用充分（+3）")
        elif citation_count >= 1:
            score += 1
            details.append("⚠️ 引用不足（+1）")
        else:
            details.append("❌ 无引用（+0）")
        
        # 基于知识库
        if not any(word in answer for word in ["不知道", "暂无相关信息"]):
            for src in sources:
                if any(entity in answer for entity in src.split()):
                    score += 1
                    break
            details.append("✅ 有知识库依据（+1）")
        
        # 完整性
        if len(answer) > 100:
            score += 1
            details.append("✅ 回答完整（+1）")
        
        return {"score": score, "max_score": 5, "details": details, "quality": "优" if score >= 4 else "良" if score >= 3 else "中" if score >= 2 else "差"}

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 RAG幻觉深度根治")
    print("=" * 60)
    
    # 1. 引用溯源
    print("\n1️⃣ 引用溯源")
    print("-" * 40)
    citation = CitationSystem()
    citation.add_document("doc_001", "AI Agent市场2024年规模达到100亿美元，同比增长45%。", "行业报告2024")
    citation.add_document("doc_002", "RAG技术可有效降低AI幻觉，准确率提升至95%。", "技术白皮书")
    
    # 模拟生成回答
    answer = "AI Agent市场2024年规模达到100亿美元，同比增长45% [^doc_001]。RAG技术可有效降低AI幻觉 [^doc_002]"
    for fact in ["AI Agent市场2024年规模达到100亿美元", "RAG技术可有效降低AI幻觉"]:
        result = citation.verify_citation(fact)
        print(f"  验证：{fact[:40]}... → {'✅ 已验证' if result['verified'] else '❌ 无依据'}")
    
    # 2. 幻觉检测
    print("\n2️⃣ 幻觉检测")
    print("-" * 40)
    detector = HallucinationDetector()
    
    # 有幻觉的答案
    hallucinated = "AI Agent市场2024年规模达到200亿美元，增长率80%。这个数据来自权威报告。"
    result = detector.check_factual_consistency(hallucinated, [
        "AI Agent市场2024年规模达到100亿美元",
        "同比增长45%"
    ])
    print(f"  输入：{hallucinated[:50]}...")
    print(f"  幻觉检测：{'❌ 发现幻觉' if result['has_hallucination'] else '✅ 正常'}")
    if result['issues']:
        for issue in result['issues']:
            print(f"    {issue}")
    
    # 正常答案
    correct = "AI Agent市场2024年规模达到100亿美元，同比增长45%"
    result2 = detector.check_factual_consistency(correct, [
        "AI Agent市场2024年规模达到100亿美元",
        "同比增长45%"
    ])
    print(f"\n  输入：{correct[:50]}...")
    print(f"  幻觉检测：{'❌ 发现幻觉' if result2['has_hallucination'] else '✅ 正常'}")
    
    # 3. 冲突检测
    print("\n3️⃣ 文档冲突检测")
    print("-" * 40)
    conflict_detector = ConflictDetector()
    docs = {
        "report_2024": {"content": "公司2024年营收100亿元"},
        "report_2023": {"content": "公司2024年营收200亿元"}
    }
    conflicts = conflict_detector.detect_conflicts(docs)
    if conflicts:
        for c in conflicts:
            print(f"  ⚠️ 冲突：[{c['between'][0]}] vs [{c['between'][1]}] → {c['conflict']}")
    
    # 4. 质量评分
    print("\n4️⃣ 生成质量评分")
    print("-" * 40)
    scorer = QualityScorer()
    score = scorer.score_response(answer, [citation.documents["doc_001"]["content"]])
    print(f"  分数：{score['score']}/{score['max_score']}")
    print(f"  质量：{score['quality']}")
    for d in score['details']:
        print(f"  {d}")
