# ===== knowledge_base/text_cleaner.py：清洗+智能切片 =====

import re

class TextCleaner:
    def __init__(self):
        # 初始化正则规则
        self.empty_line_pattern = re.compile(r"\n\s*\n")
        self.multi_space_pattern = re.compile(r"\s+")
        # 页码、页眉页脚、多余符号过滤
        self.noise_pattern = re.compile(
            r"^\d{1,5}$|第\s*\d+\s*页|页码\s*\d+|Page\s*\d+|"
            r"本文件仅供参考|版权所有|未经授权不得转载|"
            r"\|+|-+|={2,}|•{2,}"
        )

    def basic_clean(self, text: str) -> str:
        """基础清洗：去空行、去多余空格、去首尾空白"""
        # 统一换行
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # 去除多行空行
        text = self.empty_line_pattern.sub("\n", text)
        # 去除首尾空白
        text = text.strip()
        return text

    def filter_noise(self, text: str) -> str:
        """过滤页码、页眉、页脚、版权、无效单行噪声"""
        lines = text.split("\n")
        clean_lines = []
        for line in lines:
            line_strip = line.strip()
            # 过滤纯数字页码、噪声短句
            if self.noise_pattern.fullmatch(line_strip):
                continue
            if len(line_strip) < 2 and not line_strip.isalpha():
                continue
            clean_lines.append(line)
        return "\n".join(clean_lines)

    def repair_broken_sentence(self, text: str) -> str:
        """修复PDF解析断行、合并残缺段落"""
        # 匹配末尾非标点换行，说明是段落被截断
        lines = text.split("\n")
        if not lines:
            return text

        new_lines = []
        cache_line = ""

        end_punct = {"。", "！", "？", ".", "!", "?", "；", ";"}

        for line in lines:
            line = line.strip()
            if not line:
                if cache_line:
                    new_lines.append(cache_line)
                    cache_line = ""
                continue

            # 当前行不是结尾句子，合并到缓存
            if line[-1] not in end_punct:
                cache_line += line + " "
            else:
                cache_line += line
                new_lines.append(cache_line)
                cache_line = ""
        # 兜底剩余缓存内容
        if cache_line:
            new_lines.append(cache_line)

        return "\n".join(new_lines)

    def smart_chunk_split(self, text: str, chunk_size=300, overlap=50) -> list:
        """
        语义智能切片：优先按段落、标点分割
        避免生硬截断句子，保证单切片语义完整
        """
        # 先按段落拆分
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            # 加入当前段落不超长度，直接合并
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n"
            else:
                # 当前块已满，存入
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n"

        # 存入最后一段
        if current_chunk:
            chunks.append(current_chunk.strip())

        # 兜底重叠拼接，防止内容碎片化
        if overlap > 0 and len(chunks) > 1:
            final_chunks = []
            for idx, chunk in enumerate(chunks):
                if idx == 0:
                    final_chunks.append(chunk)
                else:
                    # 取上一段末尾重叠内容
                    prev = chunks[idx-1]
                    overlap_text = prev[-overlap:] if len(prev) > overlap else prev
                    new_chunk = overlap_text + "..." + chunk
                    final_chunks.append(new_chunk)
            return final_chunks

        return chunks

    def full_clean(self, text: str) -> str:
        """完整清洗流水线"""
        text = self.basic_clean(text)
        text = self.filter_noise(text)
        text = self.repair_broken_sentence(text)
        return text

# 全局单例
cleaner = TextCleaner()
