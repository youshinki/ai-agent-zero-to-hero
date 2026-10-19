#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第29篇配套完整项目代码 · commercial_wrapper.py
AI Agent 商业化封装器：四层商业化净化

  1. 去开发化：清除调试日志、分数、索引、技术标注
  2. 输出标准化：商用排版、分段、重点
  3. 异常兜底化：所有异常友好提示
  4. 体验产品化：干净、稳定、规整

不改动原有内核，通过 COMMERCIAL_MODE 一键切换开发/商业双模式。
==========================================================================
"""

import re
import traceback

from agent_core import agent
from knowledge_base.core.kb_core import kb
from knowledge_base.core.memory_core import memory


# 商业模式总开关：开发时 False（保留调试信息），交付时 True
COMMERCIAL_MODE = True


class CommercialAgentWrapper:
    def __init__(self):
        self.kb = kb
        self.memory = memory
        self.agent = agent
    
    # ---------------- 第一层：去开发化 ----------------
    def clean_debug_info(self, text: str) -> str:
        if not COMMERCIAL_MODE:
            return text
        text = re.sub(r"（综合匹配分：[\d\.\-]+(?:，[^）]*)?）", "", text)
        text = re.sub(r"片段\d+(?:（[^）]*）)?", "", text)
        text = re.sub(r"【高精度知识库检索结果】", "", text)
        text = re.sub(r"来源文档：.+?\n", "", text)
        text = re.sub(r"核心内容：", "", text)
        text = re.sub(r"\[来源：[^\]]+\]", "", text)
        text = re.sub(r"\[引用\d+\]", "", text)  # 可选：商业版隐藏内部引用编号
        text = re.sub(r"【参考知识库片段（带溯源）】", "", text)
        text = re.sub(r"（这是来自记忆库的个性化回答[^）]*）", "", text)
        text = re.sub(r"\n{2,}", "\n", text)
        return text.strip()
    
    # ---------------- 第二层：商用排版 ----------------
    def format_commercial_output(self, answer: str) -> str:
        if not COMMERCIAL_MODE:
            return answer
        # 按句号/问号/感叹号分段
        sentences = re.split(r"(?<=[。！？])", answer)
        lines = [s.strip() for s in sentences if s.strip()]
        return "\n".join(lines)
    
    # ---------------- 第三层：异常兜底 ----------------
    def safe_answer(self, user_input: str) -> dict:
        try:
            result = self.agent.run(user_input, [])
            raw = result.get("final_answer", "")
            
            clean = self.clean_debug_info(raw)
            final = self.format_commercial_output(clean)
            
            # 空输出兜底
            if not final.strip():
                return self._friendly("empty")
            
            # 自动沉淀记忆
            try:
                self.memory.add_chat_memory(user_input, final)
            except Exception:
                pass
            
            return {
                "success": True,
                "answer": final,
                "quality": result.get("quality"),
            }
        except Exception as e:
            if not COMMERCIAL_MODE:
                traceback.print_exc()
                return {"success": False, "answer": f"[DEBUG] {e}"}
            return self._friendly("error")
    
    def _friendly(self, kind: str) -> dict:
        """商业级友好提示（不暴露任何代码信息）"""
        messages = {
            "error": "抱歉，当前网络或系统繁忙，请稍后再次尝试提问。",
            "empty": "抱歉，暂未查询到相关内容。您可以尝试换一种问法，或联系管理员补充资料。",
        }
        return {"success": False, "answer": messages.get(kind, messages["error"])}


commercial_agent = CommercialAgentWrapper()
