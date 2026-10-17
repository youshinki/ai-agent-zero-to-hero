class CommercialPrivacy:
    def __init__(self):
        # 商用隐私总开关
        self.privacy_mode = True

    def forbid_external_leak(self, query: str) -> bool:
        """
        隐私拦截：禁止外部试探、禁止资料外泄
        拦截询问知识库内部文件、源码、资料地址等敏感问题
        """
        if not self.privacy_mode:
            return True

        sensitive_keys = [
            "文件位置", "存储路径", "源码", "代码", "原始文件",
            "导出资料", "下载文件", "知识库文件", "本地路径"
        ]

        for key in sensitive_keys:
            if key in query:
                return False
        return True

    def safe_reply_filter(self, query: str, answer: str) -> str:
        """商用安全过滤，屏蔽所有内部开发、路径、源码相关信息"""
        if not self.forbid_external_leak(query):
            return "抱歉，无法提供相关查询内容，仅支持业务资料问答。"
        return answer

# 隐私防护单例
privacy_safe = CommercialPrivacy()
