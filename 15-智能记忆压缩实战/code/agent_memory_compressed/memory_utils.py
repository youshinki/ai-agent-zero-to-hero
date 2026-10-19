#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第15篇配套完整项目代码 · memory_utils.py
智能记忆压缩工具：
  - count_message_tokens：估算历史token
  - compress_history：保留近期完整，远期压缩为摘要（文章第四章）
==========================================================================
"""

import re
from typing import Dict, List

from config import (
    COMPRESS_THRESHOLD, KEEP_RECENT, USE_MOCK, MODEL_NAME,
    MODEL_API_KEY, MODEL_BASE_URL,
)


def count_message_tokens(msg_list: List[Dict]) -> int:
    """粗略估算历史token数（中文按字符、按1.5倍系数估算）"""
    total = 0
    for item in msg_list:
        total += len(item.get("content", ""))
    return int(total * 1.5)


# ======================================================================
# 摘要生成（真实 / 模拟双模式）
# ======================================================================

def _llm_summarize(text: str) -> str:
    """调用LLM生成摘要"""
    if USE_MOCK:
        return _mock_summarize(text)
    from openai import OpenAI
    client = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)
    prompt = f"""请对以下历史对话进行极致精简摘要：
1. 保留用户核心身份、需求、设定、关键结论
2. 删除客套话、重复话、冗余对话
3. 输出结构化总结，方便后续AI接续对话
4. 尽量短、信息密度最高
历史对话：
{text}
"""
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content


def _mock_summarize(text: str) -> str:
    """模拟摘要：优先保留身份/偏好等关键信息，再补充少量要点"""
    critical = []   # 身份、偏好等必须保留
    points = []     # 一般要点

    # 身份
    m = re.search(r"我(?:是|叫)([^，。；\n]{1,30})", text)
    if m:
        critical.append(f"用户身份：{m.group(1)}")

    # 偏好（允许省略"我"）
    for m in re.finditer(r"(?:我)?(?:喜欢|偏好|希望|倾向|习惯)([^，。；\n]{1,40})", text):
        critical.append(f"用户偏好：{m.group(1)}")

    # 关键结论（限制数量，避免挤占关键信息）
    for line in text.split("\n"):
        if any(k in line for k in ["结论", "决定", "确定", "目标是", "计划"]):
            line = line.strip()
            if 4 <= len(line) <= 60:
                points.append(f"要点：{line}")

    # 只保留少量要点（信息密度高，避免摘要膨胀）
    points = points[:3]

    # 去重
    seen = set()
    uniq = []
    for p in critical + points:
        if p not in seen:
            seen.add(p)
            uniq.append(p)

    if not uniq:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        uniq = [f"要点：{l[:40]}" for l in lines[:2]] or ["（无显著要点）"]
    return "\n".join(uniq)


# ======================================================================
# 核心：智能压缩
# ======================================================================

def compress_history(history_list: List[Dict]) -> List[Dict]:
    """智能压缩：
    - 历史不足阈值：原样返回
    - 超过阈值：远期对话 → 摘要(system)，最近KEEP_RECENT条完整保留
    """
    if not history_list or len(history_list) < COMPRESS_THRESHOLD:
        return history_list

    old_history = history_list[:-KEEP_RECENT]
    recent_history = history_list[-KEEP_RECENT:]

    concat_text = ""
    for item in old_history:
        role = "用户" if item.get("role") == "user" else "AI"
        concat_text += f"{role}：{item.get('content', '')}\n"

    summary = _llm_summarize(concat_text)
    compressed_item = {
        "role": "system",
        "content": f"【历史对话摘要】{summary}",
    }
    return [compressed_item] + recent_history


def build_context(history_list: List[Dict], max_chars: int = 2000) -> str:
    """把历史拼成上下文字符串（自动截断保护）"""
    lines = []
    for item in history_list:
        role = "用户" if item.get("role") == "user" else ("系统" if item.get("role") == "system" else "AI")
        lines.append(f"{role}：{item.get('content', '')}")
    text = "\n".join(lines)
    if len(text) > max_chars:
        # 保留开头(摘要) + 结尾(最近对话)
        half = max_chars // 2
        text = text[:half] + "\n...（中间省略）...\n" + text[-half:]
    return text


def compression_stats(history_list: List[Dict]) -> Dict:
    """压缩前后统计（用于验证效果）"""
    before = count_message_tokens(history_list)
    compressed = compress_history(history_list)
    after = count_message_tokens(compressed)
    ratio = (1 - after / before) * 100 if before else 0
    return {
        "msgs_before": len(history_list),
        "msgs_after": len(compressed),
        "tokens_before": before,
        "tokens_after": after,
        "reduction": f"{ratio:.1f}%",
    }
