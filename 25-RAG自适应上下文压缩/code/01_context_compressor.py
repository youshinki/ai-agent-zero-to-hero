# ===== context_compressor.py：自适应上下文压缩 =====

import re

class ContextCompressor:
    def __init__(self):
        # 正则匹配冗余格式文本
        self.score_pattern = re.compile(r"（综合匹配分：[\d\.]+）")
        self.source_pattern = re.compile(r"来源文档：.+?\n")
        self.prefix_pattern = re.compile(r"【高精度知识库检索结果】\n")

    def clean_rag_format(self, text: str) -> str:
        """清理RAG检索自带冗余格式内容"""
        text = self.prefix_pattern.sub("", text)
        text = self.score_pattern.sub("", text)
        text = self.source_pattern.sub("", text)
        # 清理多余空行
        text = re.sub(r"\n+", "\n", text)
        return text.strip()

    def remove_repeat_sentence(self, text: str) -> str:
        """去除重复语句，精简冗余表述"""
        lines = text.split("\n")
        unique_lines = []
        for line in lines:
            if line.strip() not in unique_lines:
                unique_lines.append(line.strip())
        return "\n".join(unique_lines)

    def adaptive_trim(self, text: str, max_token: int = 1800) -> str:
        """
        自适应文本裁剪
        按字符近似Token换算，1中文≈2Token
        保证句子完整，不生硬截断
        """
        # 近似字符阈值
        max_char = int(max_token / 2)
        if len(text) <= max_char:
            return text

        # 按完整句子截断，优先保留前文核心信息
        end_punct = {"。", "！", "？", ".", "!", "?", "；", ";"}
        trim_text = text[:max_char]

        # 从末尾往前找完整句结尾，防止断句
        last_end_idx = 0
        for idx, char in enumerate(trim_text):
            if char in end_punct:
                last_end_idx = idx + 1

        if last_end_idx > 0:
            trim_text = trim_text[:last_end_idx]
        else:
            # 无标点兜底，按段落截断
            trim_text = trim_text.rsplit("\n", 1)[0]

        return trim_text.strip()

    def compress(self, rag_context: str, max_token: int = 1800) -> str:
        """
        一站式上下文压缩入口
        :param rag_context: 原始检索拼接文本
        :param max_token: 模型最大接收Token
        :return: 压缩后无损上下文
        """
        # 1. 清理格式冗余
        text = self.clean_rag_format(rag_context)
        # 2. 去除重复语句
        text = self.remove_repeat_sentence(text)
        # 3. 自适应长度裁剪
        text = self.adaptive_trim(text, max_token)
        return text

# 全局单例
compressor = ContextCompressor()
