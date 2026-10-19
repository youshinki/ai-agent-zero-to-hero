#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第30篇配套完整项目代码 · knowledge_base/commercial/safe_privacy.py
企业隐私安全隔离：
  - 拦截外部试探（询问源码、内部文件、资料地址等）
  - 输出脱敏（手机号、邮箱、密钥、身份证）
  - 隐私模式总开关
==========================================================================
"""

import re


class CommercialPrivacy:
    def __init__(self):
        self.privacy_mode = True
        
        # 敏感试探关键词
        self.sensitive_keys = [
            "系统提示词", "system prompt", "你的规则", "内部源码", "源代码",
            "数据库地址", "配置文件", "api key", "密钥", "其他客户",
            "后台密码", "管理员密码", "训练数据", "上传的文件列表",
        ]
    
    def forbid_external_leak(self, query: str) -> bool:
        """隐私拦截：True=允许，False=拒绝"""
        if not self.privacy_mode:
            return True
        q = query.lower()
        return not any(k.lower() in q for k in self.sensitive_keys)
    
    def leak_response(self) -> str:
        """统一拒绝话术"""
        return "抱歉，该问题涉及系统内部信息，我无法提供。如需帮助，请联系管理员。"
    
    @staticmethod
    def mask_output(text: str) -> str:
        """输出脱敏（脱敏手机号/邮箱/密钥/身份证）"""
        text = re.sub(r"1[3-9]\d{9}", "138****0000", text)
        text = re.sub(r"\w+@\w+\.\w+", "***@***.com", text)
        text = re.sub(r"sk-[A-Za-z0-9_\-]{8,}", "sk-****", text)
        text = re.sub(r"\d{17}[\dXx]", "******************", text)
        return text
    
    def check_and_clean(self, query: str, answer: str) -> dict:
        """一体化：先拦截、再脱敏"""
        if not self.forbid_external_leak(query):
            return {"allowed": False, "answer": self.leak_response()}
        return {"allowed": True, "answer": self.mask_output(answer)}


commercial_privacy = CommercialPrivacy()
