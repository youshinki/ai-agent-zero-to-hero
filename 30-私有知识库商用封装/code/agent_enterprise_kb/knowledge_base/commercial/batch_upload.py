#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第30篇配套完整项目代码 · knowledge_base/commercial/batch_upload.py
企业批量入库工具：批量导入 / 自动去重 / 增量更新
==========================================================================
"""

import os

from knowledge_base.core.kb_core import kb
from config import UPLOAD_DOC_PATH


SUPPORT_SUFFIX = (".pdf", ".docx", ".doc", ".txt", ".md")


class CommercialBatchUpload:
    def __init__(self):
        self.doc_dir = UPLOAD_DOC_PATH
        os.makedirs(self.doc_dir, exist_ok=True)
    
    def batch_import_all(self) -> dict:
        """批量导入目录下所有文档，自动增量更新"""
        if not os.path.isdir(self.doc_dir):
            return {"success": False, "count": 0, "detail": "企业资料目录不存在"}
        
        imported, skipped, failed = 0, 0, []
        for file_name in sorted(os.listdir(self.doc_dir)):
            suffix = os.path.splitext(file_name)[1].lower()
            if suffix not in SUPPORT_SUFFIX:
                continue
            file_path = os.path.join(self.doc_dir, file_name)
            try:
                result = kb.single_file_increment_update(file_path)
                if result["status"] == "updated":
                    imported += 1
                elif result["status"] == "unchanged":
                    skipped += 1
                else:
                    failed.append(f"{file_name}：{result['message']}")
            except Exception as e:
                failed.append(f"{file_name}：{e}")
        
        return {
            "success": len(failed) == 0,
            "count": imported,
            "skipped": skipped,
            "failed": failed,
            "detail": f"企业批量入库完成：成功导入 {imported} 份，跳过 {skipped} 份，失败 {len(failed)} 份",
        }
    
    def clear_docs(self) -> str:
        """清空知识库（企业资料重置专用）"""
        return kb.clear_kb()


batch_uploader = CommercialBatchUpload()
