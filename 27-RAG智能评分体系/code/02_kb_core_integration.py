"""
在 LocalKnowledgeBase 中接入评分器：先在 kb_core.py 顶部导入，再新增下面的查询方法。
"""

from .rag_evaluator import evaluator

def evaluate_qa_quality(self, query: str, answer: str, retrieve_text: str) -> dict:
    """
    对外暴露：问答质量智能评分接口
    """
    return evaluator.evaluate(query, retrieve_text, answer)
