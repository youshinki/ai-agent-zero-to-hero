#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第57篇配套完整项目代码 · prompt_chain.py
Prompt Chain 高级设计：条件分支链式编排、Chain 与 Agent 边界

  1. ChainStep 定义（prompt 模板 + 校验）
  2. 条件分支路由
  3. 顺序链执行
  4. 校验失败重试 / 降级
  5. Chain 与 Agent 的边界对比
==========================================================================
"""

from typing import Any, Callable, Dict, List, Optional


# ======================================================================
# 一、步骤定义
# ======================================================================

class ChainStep:
    def __init__(self, name: str, prompt: str,
                 validate: Optional[Callable[[str], bool]] = None,
                 fallback: Optional[str] = None,
                 max_retry: int = 1):
        self.name = name
        self.prompt = prompt
        self.validate = validate
        self.fallback = fallback
        self.max_retry = max_retry


# ======================================================================
# 二、模拟 LLM
# ======================================================================

class MockLLM:
    def run(self, prompt: str) -> str:
        if "分类" in prompt:
            if "退款" in prompt or "退钱" in prompt:
                return "售后"
            if "价格" in prompt or "多少钱" in prompt:
                return "售前"
            return "其他"
        if "提取" in prompt:
            return '{"intent": "售后", "product": "耳机"}'
        if "回复" in prompt:
            return "您好，已收到您的售后请求，我们会在24小时内处理。"
        return f"[模拟输出] {prompt[:30]}"


# ======================================================================
# 三、Chain 执行器
# ======================================================================

class PromptChain:
    def __init__(self, llm=None):
        self.llm = llm or MockLLM()
        self.steps: List[ChainStep] = []
        self.trace: List[Dict] = []
    
    def add(self, step: ChainStep) -> "PromptChain":
        self.steps.append(step)
        return self
    
    def run(self, inputs: Dict[str, Any]) -> Dict:
        self.trace = []
        context = dict(inputs)
        out = ""
        ok = True
        
        for step in self.steps:
            prompt = step.prompt.format(**context)
            result, attempts = "", 0
            for attempts in range(1, step.max_retry + 2):
                result = self.llm.run(prompt)
                if step.validate is None or step.validate(result):
                    break
                if attempts > step.max_retry:
                    result = step.fallback or result
                    ok = False
                    break
            
            self.trace.append({"step": step.name, "attempts": attempts,
                               "passed": step.validate is None or
                               (step.validate and step.validate(result)),
                               "output": result[:60]})
            out = result
            context["last"] = out
            context[step.name] = out
        
        return {"inputs": inputs, "output": out, "ok": ok, "trace": self.trace}


# ======================================================================
# 四、条件分支
# ======================================================================

class BranchChain:
    """按分类结果路由到不同子链"""
    
    def __init__(self):
        self.classifier = PromptChain()
        self.classifier.add(ChainStep(
            "classify", "请对用户问题分类：{question}",
            validate=lambda x: x in ("售前", "售后", "其他"),
        ))
        self.branches = {
            "售前": self._sales_chain(),
            "售后": self._after_sales_chain(),
            "其他": self._general_chain(),
        }
    
    def _sales_chain(self) -> PromptChain:
        c = PromptChain()
        c.add(ChainStep("extract", "提取售前意图：{last}",
                        validate=lambda x: x.startswith("{")))
        c.add(ChainStep("reply", "生成售前回复：{last}"))
        return c
    
    def _after_sales_chain(self) -> PromptChain:
        c = PromptChain()
        c.add(ChainStep("extract", "提取售后意图：{last}",
                        validate=lambda x: x.startswith("{")))
        c.add(ChainStep("reply", "生成售后回复：{last}"))
        return c
    
    def _general_chain(self) -> PromptChain:
        c = PromptChain()
        c.add(ChainStep("reply", "生成通用回复：{last}"))
        return c
    
    def run(self, question: str) -> Dict:
        cls = self.classifier.run({"question": question})
        category = cls["output"]
        branch = self.branches.get(category, self.branches["其他"])
        result = branch.run({"question": question, "last": category})
        return {"question": question, "category": category,
                "branch_trace": result["trace"],
                "answer": result["output"], "ok": result["ok"]}


# ======================================================================
# 五、Chain vs Agent
# ======================================================================

COMPARISON = {
    "Chain": {
        "控制": "开发者固定步骤与分支",
        "优点": "可预测、稳定、成本低、易测试",
        "缺点": "灵活性低，无法处理未预设路径",
        "适合": "流程固定的业务（客服分流/内容生产管线）",
    },
    "Agent": {
        "控制": "模型自主规划与决策",
        "优点": "灵活，可处理开放任务",
        "缺点": "不稳定、成本高、难测试",
        "适合": "开放复杂任务（调研/多工具协同）",
    },
}


def demo():
    print("=" * 66)
    print("🔗 Prompt Chain 高级设计演示")
    print("=" * 66)
    
    print("\n[1] 顺序链：")
    chain = PromptChain()
    chain.add(ChainStep("classify", "请对用户问题分类：{question}",
                        validate=lambda x: x in ("售前", "售后", "其他")))
    chain.add(ChainStep("extract", "提取意图：{last}",
                        validate=lambda x: x.startswith("{")))
    chain.add(ChainStep("reply", "生成回复：{last}"))
    r = chain.run({"question": "我要退款，耳机坏了"})
    print(f"   输出：{r['output']}")
    print(f"   追踪：{r['trace']}")
    
    print("\n[2] 条件分支：")
    bc = BranchChain()
    for q in ["这个耳机多少钱", "我要退款", "你们公司在哪里"]:
        r = bc.run(q)
        print(f"\n   问：{q}")
        print(f"   分类：{r['category']} → 答案：{r['answer'][:50]}")
    
    print("\n[3] Chain vs Agent：")
    for name, info in COMPARISON.items():
        print(f"   {name}：{info['控制']}｜适合：{info['适合']}")


if __name__ == "__main__":
    demo()
