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
from knowledge_base.memory_core import memory
from tools.tool_manager import create_default_tools


tool_manager = create_default_tools()


# 商用级引用规则（文章第五章）
def build_fusion_context(user_input: str, ref_text: str = "") -> str:
    """构建双引擎融合上下文

    1. 用户偏好档案
    2. 相关/近期长期记忆
    3. 私有知识库资料
    个性化问题偏重记忆，专业问题偏重知识库。
    """
    profile_ctx = memory.get_user_profile()
    mem_ctx = memory.search_memory(user_input, top_k=3) or memory.get_recent_memory(top_k=4)

    fusion = "# 用户专属信息与私有知识上下文\n"
    if profile_ctx:
        fusion += profile_ctx + "\n"
    fusion += mem_ctx + "\n"
    if ref_text:
        fusion += ref_text + "\n"
    return fusion


def extract_profile(user_input: str):
    """从用户话语中抽取身份/偏好，写入长期记忆"""
    patterns = [
        (r"我(?:是|叫)([^，。；\n]{1,20})", "身份"),
        (r"(?:我)?(?:喜欢|偏好|习惯|希望)([^，。；\n]{1,30})", "偏好"),
        (r"我的([^，。；\n]{1,10})是([^，。；\n]{1,20})", None),
    ]
    for pattern, label in patterns:
        m = re.search(pattern, user_input)
        if m:
            if label:
                memory.update_user_profile(label, m.group(1).strip())
            else:
                memory.update_user_profile(m.group(1).strip(), m.group(2).strip())


RAG_SYSTEM_PROMPT = """
你是基于私有知识库的专业智能问答助手，必须严格遵守以下引用规则：
1. 所有回答内容必须严格基于参考知识库片段，禁止编造、禁止脑补、禁止使用外部模型知识。
2. 回答中每一处关键结论、数据、流程、规则，都需要标注对应引用序号，格式为【引用1】【引用2】。
3. 若多个片段综合得出结论，需要同时标注所有对应来源。
4. 若知识库内容不足以回答问题，必须如实说明「当前知识库无相关内容」，禁止强行回答。
5. 回答结尾必须自动汇总【参考文献列表】，去重展示所有用到的文档来源。
6. 禁止输出知识库以外的知识，杜绝一切幻觉。
"""


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
        # 带引用的知识库上下文
        if "参考知识库片段" in prompt or "[引用1]" in prompt:
            question = ""
            if "用户问题：" in prompt:
                question = prompt.split("用户问题：", 1)[1].split("\n")[0].strip()
            # 提取引用片段
            import re as _re
            refs = _re.findall(r"\[引用(\d+)\] 来源文档：([^\n]+)\n内容：([^\n]+)", prompt)
            if not refs:
                return f"当前知识库无与「{question}」相关的内容。"
            parts = []
            for rid, src, content in refs[:3]:
                parts.append(f"{content.strip()[:80]}（【引用{rid}】）")
            body = "；".join(parts)
            return (f"根据知识库资料，回答「{question}」：{body}。\n\n"
                    f"以上结论均来自私有文档，未使用外部知识。")
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

        # 4. 清空长期记忆
        if "清空记忆" in user_input or "忘记我" in user_input:
            return {"action": "clear_memory", "final_answer": memory.clear_memory()}

        # 5. 清空知识库
        if "清空知识库" in user_input or "删除知识库" in user_input:
            result = tool_manager.execute_tool("kb_clear", {})
            return {"action": "clear", "final_answer": result}
        
        # 3. 提前抽取用户档案（个性化信息直接沉淀）
        extract_profile(user_input)
        
        # 4. 问答任务：检索 + 溯源绑定
        print("   🔍 检索私有知识库（绑定溯源）...")
        ref_text, ref_map = kb.build_citation_context(user_input, top_k=3)
        if ref_map:
            print(f"   命中 {len(ref_map)} 个片段：" +
                  "、".join(f"[引用{k}]{v['source']}" for k, v in ref_map.items()))
        else:
            print("   知识库为空或无相关内容")
        
        if not ref_map:
            # 知识库无命中：使用长期记忆进行个性化对话，并沉淀本次对话
            profile = memory.get_user_profile()
            recent = memory.get_recent_memory(top_k=4)
            if self.llm.use_mock:
                if "记得" in user_input or "身份" in user_input or "偏好" in user_input:
                    answer = (f"根据长期记忆，{profile.strip() or '暂无档案信息。'}\n"
                              f"（这是来自记忆库的个性化回答，未使用知识库内容。）")
                else:
                    answer = (f"（知识库暂无相关内容）已记录你的信息。"
                              f"当前偏好档案：{profile.strip() or '暂无'}。")
            else:
                answer = self.llm.chat(f"""{RAG_SYSTEM_PROMPT}

{profile}
{recent}

用户问题：{user_input}

注意：知识库未检索到相关内容；如属个性化/身份类问题，可基于用户记忆回答；
其余情况必须如实说明「当前知识库无相关内容」。""", system=RAG_SYSTEM_PROMPT)
            memory.add_chat_memory(user_input, answer)
            return {"action": "chat", "refs": {}, "memory_stats": memory.stats(),
                    "final_answer": answer}
        
        # 4. 双引擎融合上下文（档案 + 记忆 + 知识库）
        fusion_ctx = build_fusion_context(user_input, ref_text)
        context_hist = f"历史对话：{build_context(self.history)}\n" if self.history else ""
        prompt = f"""{RAG_SYSTEM_PROMPT}

{context_hist}
{fusion_ctx}

用户问题：{user_input}"""
        
        answer = self.llm.chat(prompt, system=RAG_SYSTEM_PROMPT)
        
        # 5. 自动汇总参考文献（去重）
        ref_summary = kb.get_ref_summary(ref_text)
        if ref_summary and "【参考文献】" not in answer:
            answer += ref_summary
        
        # 5.5 记忆沉淀：写入长期记忆
        extract_profile(user_input)
        memory.add_chat_memory(user_input, answer)
        
        # 6. 自动四维评分与优化建议（问答+自检双闭环）
        # 评分输入剔除引用格式标签，只用正文内容评分，避免格式噪声
        import re as _re
        score_text = _re.sub(r"\[引用\d+\]|来源文档：[^\n]*|内容：|【参考知识库片段（带溯源）】", "",
                             ref_text)
        quality = kb.evaluate_qa_quality(user_input, answer, score_text)
        
        return {
            "action": "qa",
            "refs": ref_map,
            "ref_text": ref_text,
            "quality": quality,
            "memory_stats": memory.stats(),
            "final_answer": answer,
        }


agent = KnowledgeAgent()
