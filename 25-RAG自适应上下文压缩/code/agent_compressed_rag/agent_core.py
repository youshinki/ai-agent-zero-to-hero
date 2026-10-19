#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第20篇配套完整项目代码 · agent_core.py
接入本地私有知识库的 Agent：
  先检索 → 后生成，答案全部源自私有文档
==========================================================================
"""

import re
import time
from typing import Any, Dict, List

from config import USE_MOCK, MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL
from memory_utils import compress_history, build_context
from knowledge_base.kb_core import kb
from tools.tool_manager import create_default_tools


tool_manager = create_default_tools()


class LLMClient:
    def __init__(self):
        self.use_mock = USE_MOCK
        self.client = None
        if not self.use_mock:
            from openai import OpenAI
            self.client = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)

    def chat(self, prompt: str, system: str = "") -> str:
        if self.use_mock:
            return self._mock(prompt)
        messages = ([{"role": "system", "content": system}] if system else [])
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(
            model=MODEL_NAME, messages=messages, temperature=0.2
        )
        return resp.choices[0].message.content

    def _mock(self, prompt: str) -> str:
        time.sleep(0.02)
        # 有知识库上下文 → 基于资料回答
        if "私有资料" in prompt or "参考资料" in prompt:
            question = ""
            for marker in ["\n用户问题：", "用户问题："]:
                if marker in prompt:
                    question = prompt.split(marker, 1)[1].split("\n")[0].strip()
                    break
            context = ""
            for marker in ["参考资料：", "私有资料："]:
                if marker in prompt:
                    context = prompt.split(marker, 1)[1].strip()
                    break
            excerpt = context.replace("\n", " ").strip()[:220]
            if not excerpt:
                return f"知识库中暂无与「{question}」相关的信息，建议先上传相关文档。"
            return (f"根据私有知识库资料，回答「{question}」：\n\n"
                    f"{excerpt}\n\n📎 以上内容全部来自私有文档，未做资料外补充。")
        return f"[模拟回答] {prompt[:50]}..."


class KnowledgeAgent:
    """接入私有知识库的Agent"""
    
    def __init__(self):
        self.history: List[Dict] = []
        self.llm = LLMClient()
    
    def load_history(self, history_list: List[Dict]):
        self.history = compress_history(history_list or [])
    
    def _is_upload_task(self, text: str) -> bool:
        return any(k in text for k in ["入库", "上传文档", "导入文档", "加入知识库"])
    
    def _extract_path(self, text: str) -> str:
        m = re.search(r"([^\s，。]+\.(?:txt|md|json|csv|pdf|docx))", text)
        return m.group(1) if m else ""
    
    def run(self, user_input: str, history_list: List[Dict]) -> Dict[str, Any]:
        self.load_history(history_list)
        print(f"\n🤖 KnowledgeAgent | {user_input}")
        
        # 1. 入库任务
        if self._is_upload_task(user_input):
            path = self._extract_path(user_input)
            if not path:
                return {"action": "upload", "success": False,
                        "final_answer": "请提供要入库的文档路径，例如 knowledge_base/upload_doc/product.txt"}
            result = tool_manager.execute_tool("kb_upload_doc", {"file_path": path})
            success = "成功" in result
            return {"action": "upload", "success": success,
                    "tool_result": result,
                    "final_answer": result}
        
        # 2. 全量扫描增量更新
        if any(k in user_input for k in ["扫描更新", "增量更新", "同步知识库", "更新知识库"]):
            result = tool_manager.execute_tool("kb_scan_update", {})
            return {"action": "scan", "final_answer": result}

        # 3. 清理孤立向量
        if any(k in user_input for k in ["清理残留", "清理孤立", "清理过期"]):
            result = tool_manager.execute_tool("kb_cleanup_orphans", {})
            return {"action": "cleanup", "final_answer": result}

        # 4. 清空知识库
        if "清空知识库" in user_input or "删除知识库" in user_input:
            result = tool_manager.execute_tool("kb_clear", {})
            return {"action": "clear", "final_answer": result}
        
        # 3. 问答任务：先检索
        print("   🔍 检索私有知识库...")
        hits = kb.search(user_input, top_k=3)
        context = kb.search_as_text(user_input, top_k=3)
        if hits:
            print(f"   命中 {len(hits)} 个片段（最高相似度 {hits[0]['score']}）")
        else:
            print("   知识库为空或无相关内容")
        
        # 4. 结合检索结果生成答案
        context_hist = f"历史对话：{build_context(self.history)}\n" if self.history else ""
        prompt = f"""你是基于私有知识库的问答助手。请严格基于参考资料作答，禁止编造。

{context_hist}
参考资料：
{context}

用户问题：{user_input}

要求：
1. 只使用参考资料中的信息
2. 资料不足时明确说明"知识库中暂无相关信息"
3. 标注来源"""
        
        answer = self.llm.chat(prompt, system="你是严谨的知识库问答助手")
        
        return {
            "action": "qa",
            "hits": [{"score": h["score"], "source": h["source"]} for h in hits],
            "final_answer": answer,
        }


agent = KnowledgeAgent()
