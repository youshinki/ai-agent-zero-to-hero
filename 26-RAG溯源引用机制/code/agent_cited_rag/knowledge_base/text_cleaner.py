#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第23篇配套完整项目代码 · knowledge_base/text_cleaner.py
文本智能清洗 + 精炼 + 智能切片（四级净化流水线）

  1. 基础清洗：去空行、多余空格
  2. 噪声过滤：页码、页眉页脚、版权、无效符号
  3. 语义修复：合并断行、修复残缺段落
  4. 智能切片：按段落/标点切分，保证语义完整
==========================================================================
"""

import re


class TextCleaner:
    def __init__(self):
        self.empty_line_pattern = re.compile(r"\n\s*\n")
        self.multi_space_pattern = re.compile(r"[ \t]{2,}")
        self.noise_pattern = re.compile(
            r"^[\-–—\s]*\d{1,5}[\-–—\s]*$"      # "- 3 -" / "12"
            r"|第\s*\d+\s*页|页码\s*\d+|Page\s*\d+"
            r"|\|+|-{3,}|={2,}|•{2,}"
        )
        # 噪声关键词（行内包含即过滤）
        self.noise_keywords = ["版权所有", "未经授权", "仅供参考", "本文件仅", "免责声明"]
    
    # ---------------- 1. 基础清洗 ----------------
    def basic_clean(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = self.empty_line_pattern.sub("\n", text)
        # 去多余空白（保留换行）
        text = "\n".join(
            self.multi_space_pattern.sub(" ", line).strip()
            for line in text.split("\n")
        )
        return text.strip()
    
    # ---------------- 2. 噪声过滤 ----------------
    def filter_noise(self, text: str) -> str:
        lines = text.split("\n")
        clean_lines = []
        for line in lines:
            s = line.strip()
            if not s:
                continue
            if self.noise_pattern.fullmatch(s):
                continue
            if any(k in s for k in self.noise_keywords):
                continue
            # 单字符无效行（保留中文/字母）
            if len(s) < 2 and not s.isalpha():
                continue
            clean_lines.append(line)
        return "\n".join(clean_lines)
    
    # ---------------- 3. 语义修复 ----------------
    def repair_broken_sentence(self, text: str) -> str:
        """合并PDF解析造成的断行"""
        lines = text.split("\n")
        if not lines:
            return text
        
        end_punct = {"。", "！", "？", ".", "!", "?", "；", ";", "：", ":"}
        new_lines, cache = [], ""
        
        for line in lines:
            line = line.strip()
            if not line:
                if cache:
                    new_lines.append(cache)
                    cache = ""
                continue
            
            # 标题行直接保留（章节标题 / markdown标题）
            is_heading = bool(re.match(
                r"^(#{1,6}\s|第[一二三四五六七八九十百\d]+[章节部分篇]|[一二三四五六七八九十]+、)",
                line))
            if is_heading:
                if cache:
                    new_lines.append(cache)
                    cache = ""
                new_lines.append(line)
                continue
            
            # 合并断行：中文标点结尾不加空格
            if cache:
                sep = "" if cache.rstrip()[-1:] in "、，,：:；;" else " "
                cache = cache.rstrip() + sep + line
            else:
                cache = line
            
            if cache[-1] in end_punct:
                new_lines.append(cache)
                cache = ""
        
        if cache:
            new_lines.append(cache)
        return "\n".join(new_lines)
    
    # ---------------- 4. 智能切片 ----------------
    def smart_chunk_split(self, text: str, chunk_size: int = 300,
                          overlap: int = 50) -> list:
        """按段落优先切分，避免生硬截断句子"""
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        chunks, current = [], ""
        
        for para in paragraphs:
            if len(current) + len(para) + 1 <= chunk_size:
                current += para + "\n"
            else:
                if current:
                    chunks.append(current.strip())
                # 单段落超长 → 按句子二次切分
                if len(para) > chunk_size:
                    sentences = re.split(r"(?<=[。！？.!?；;])", para)
                    buf = ""
                    for sent in sentences:
                        if len(buf) + len(sent) <= chunk_size:
                            buf += sent
                        else:
                            if buf:
                                chunks.append(buf.strip())
                            buf = sent
                    current = buf + "\n" if buf else ""
                else:
                    current = para + "\n"
        
        if current.strip():
            chunks.append(current.strip())
        
        # 重叠拼接（防止内容碎片化导致上下文丢失）
        if overlap > 0 and len(chunks) > 1:
            final = [chunks[0]]
            for idx in range(1, len(chunks)):
                prev = chunks[idx - 1]
                overlap_text = prev[-overlap:] if len(prev) > overlap else prev
                final.append(overlap_text + "..." + chunks[idx])
            return final
        
        return chunks
    
    # ---------------- 完整流水线 ----------------
    def full_clean(self, text: str) -> str:
        text = self.basic_clean(text)
        text = self.filter_noise(text)
        text = self.repair_broken_sentence(text)
        return text
    
    def clean_and_split(self, text: str, chunk_size: int = 300,
                        overlap: int = 50) -> list:
        return self.smart_chunk_split(self.full_clean(text), chunk_size, overlap)


cleaner = TextCleaner()
