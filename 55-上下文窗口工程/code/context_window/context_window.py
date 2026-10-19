#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第55篇配套完整项目代码 · context_window.py
上下文窗口工程：让长对话不丢失关键信息

  1. Token 预算管理
  2. 滑动窗口（保留最近N轮）
  3. 摘要压缩（远期对话摘要）
  4. 优先级保留（系统/摘要/最近/关键信息）
  5. 组装与截断兜底
==========================================================================
"""

import re
from typing import Dict, List


# ======================================================================
# 一、Token 估算
# ======================================================================

def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    zh = len(re.findall(r"[\u4e00-\u9fa5]", text))
    return int(zh * 1.5 + (len(text) - zh) * 0.3) + 1


# ======================================================================
# 二、上下文管理器
# ======================================================================

class ContextManager:
    def __init__(self, max_tokens: int = 2000, keep_recent: int = 6):
        self.max_tokens = max_tokens
        self.keep_recent = keep_recent
        self.summary = ""   # 远期摘要
        self.system = ""    # 系统提示词
        self.messages: List[Dict] = []
    
    def set_system(self, text: str):
        self.system = text
    
    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
    
    # ---------------- 摘要 ----------------
    def summarize_old(self):
        """把超出 keep_recent 的旧消息压缩成摘要"""
        if len(self.messages) <= self.keep_recent:
            return
        old = self.messages[:-self.keep_recent]
        recent = self.messages[-self.keep_recent:]
        
        # 提取关键信息（身份/偏好/结论）
        points = []
        for m in old:
            text = m["content"]
            for pat, label in [
                (r"我(?:是|叫)([^，。；\n]{1,20})", "身份"),
                (r"(?:我)?(?:喜欢|偏好|需要)([^，。；\n]{1,20})", "偏好"),
                (r"(?:结论|决定|确认|目标是)[：:]([^，。；\n]{1,30})", "结论"),
            ]:
                mt = re.search(pat, text)
                if mt:
                    points.append(f"{label}：{mt.group(1)}")
        
        summary_text = "；".join(dict.fromkeys(points)) or "（历史对话已省略）"
        self.summary = f"【历史摘要】{summary_text}"
        self.messages = recent
    
    # ---------------- 组装 ----------------
    def build(self) -> Dict:
        self.summarize_old()
        
        priority = []
        if self.system:
            priority.append({"role": "system", "content": self.system})
        if self.summary:
            priority.append({"role": "system", "content": self.summary})
        
        # 先放关键信息（摘要），再从最近往前放消息
        selected = []
        used = sum(estimate_tokens(x["content"]) for x in priority)
        
        for msg in reversed(self.messages):
            t = estimate_tokens(msg["content"])
            if used + t > self.max_tokens:
                break
            selected.append(msg)
            used += t
        selected.reverse()
        
        full = priority + selected
        return {
            "messages": full,
            "tokens": used,
            "max_tokens": self.max_tokens,
            "truncated": len(selected) < len(self.messages),
            "summary": self.summary,
        }


# ======================================================================
# 三、演示
# ======================================================================

def demo():
    print("=" * 66)
    print("🪟 上下文窗口工程演示")
    print("=" * 66)
    
    cm = ContextManager(max_tokens=400, keep_recent=6)
    cm.set_system("你是一个AI助手，请记住用户偏好。")
    
    conversations = [
        ("user", "我是一名AI开发者，喜欢简洁的回答"),
        ("assistant", "好的，已记住。"),
        ("user", "帮我分析一下RAG的检索流程"),
        ("assistant", "RAG流程：加载→分块→向量化→检索→生成。"),
        ("user", "那重排序怎么做"),
        ("assistant", "重排序：扩召Top10→双权重重排→去重融合。"),
        ("user", "上下文压缩呢"),
        ("assistant", "压缩：去冗余→去重→按Token阈值裁剪。"),
        ("user", "好的，继续讲工具调用"),
        ("assistant", "工具调用：模型决策→代码执行→结果回填。"),
    ]
    for role, content in conversations:
        cm.add(role, content)
    
    print(f"\n原始消息：{len(cm.messages)} 条，估算 "
          f"{sum(estimate_tokens(m['content']) for m in cm.messages)} token")
    
    ctx = cm.build()
    print(f"\n组装后：{len(ctx['messages'])} 条，{ctx['tokens']} token"
          f"（上限{ctx['max_tokens']}）")
    print(f"是否截断：{ctx['truncated']}")
    print(f"摘要：{ctx['summary']}")
    print(f"\n组装内容：")
    for m in ctx["messages"]:
        print(f"   [{m['role']}] {m['content'][:40]}")
    
    assert ctx["tokens"] <= ctx["max_tokens"]
    assert ctx["summary"]


if __name__ == "__main__":
    demo()
