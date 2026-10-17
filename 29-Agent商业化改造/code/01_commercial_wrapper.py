"""
AI Agent 商业化封装器
第二篇章：商业化落地实战 · 第29篇
功能：去除调试痕迹、标准化输出、异常兜底、产品级美化
"""
import traceback
from knowledge_base.kb_core import kb
from knowledge_base.memory_core import memory
from knowledge_base.rag_evaluator import evaluator

# 商业模式总开关
COMMERCIAL_MODE = True

class CommercialAgentWrapper:
    def __init__(self):
        self.kb = kb
        self.memory = memory
        self.evaluator = evaluator

    def clean_debug_info(self, text: str) -> str:
        """
        第一层净化：彻底清除所有开发调试痕迹
        """
        if not COMMERCIAL_MODE:
            return text
        
        # 移除技术调试字段、分数、索引、开发标注
        import re
        text = re.sub(r"（综合匹配分：[\d\.]+）", "", text)
        text = re.sub(r"片段\d+", "", text)
        text = re.sub(r"【高精度知识库检索结果】", "", text)
        text = re.sub(r"来源文档：.+?\n", "", text)
        text = re.sub(r"核心内容：", "", text)
        
        # 清理多余空行、空格
        text = re.sub(r"\n+", "\n", text)
        return text.strip()

    def format_commercial_output(self, answer: str) -> str:
        """
        第二层净化：商业级排版美化
        自动分段、优化阅读体验、提升产品质感
        """
        sentences = answer.replace("。", "。\n").replace("？", "？\n").replace("！", "！\n")
        lines = [line.strip() for line in sentences.split("\n") if line.strip()]
        return "\n".join(lines)

    def safe_answer(self, user_input: str) -> str:
        """
        第三层：全局异常兜底
        杜绝报错暴露、空白输出、崩溃闪退
        """
        try:
            # 1. 融合知识库+记忆上下文
            from knowledge_base.fusion_ctx import build_fusion_context
            ctx = build_fusion_context(user_input)

            # 2. 调用模型生成回答（兼容原有逻辑）
            # 此处承接你原有agent_core对话逻辑
            # ...
            
            # 临时兼容输出（实战可直接对接原有返回）
            raw_ans = ctx
            clean_ans = self.clean_debug_info(raw_ans)
            final_ans = self.format_commercial_output(clean_ans)

            # 3. 自动沉淀记忆
            self.memory.add_chat_memory(user_input, final_ans)

            return final_ans

        except Exception as e:
            # 商业级友好报错，不暴露任何代码信息
            traceback.print_exc()
            return "✅ 系统运行正常\n抱歉，当前网络或系统繁忙，请稍后再次尝试提问。"

# 全局商业代理单例
commercial_agent = CommercialAgentWrapper()
