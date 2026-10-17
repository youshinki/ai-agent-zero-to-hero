import os
from core.kb_core import kb
from core.parse_doc import parse_file
from core.text_cleaner import clean_text

class CommercialBatchUpload:
    def __init__(self):
        # 企业文档存放目录
        self.doc_dir = "knowledge_base/data/"
        os.makedirs(self.doc_dir, exist_ok=True)

    def batch_import_all(self):
        """批量导入目录下所有文档，自动增量更新"""
        support_suffix = [".pdf", ".docx", ".doc", ".txt", ".md"]
        import_count = 0

        for file_name in os.listdir(self.doc_dir):
            suffix = os.path.splitext(file_name)[1].lower()
            if suffix not in support_suffix:
                continue

            file_path = os.path.join(self.doc_dir, file_name)
            try:
                # 解析+清洗商用级文本
                raw_content = parse_file(file_path)
                clean_content = clean_text(raw_content)

                # 增量入库，自动去重
                kb.add_document(
                    source_name=file_name,
                    content=clean_content
                )
                import_count += 1
                print(f"【商用入库成功】{file_name}")
            except Exception as e:
                print(f"【入库失败】{file_name}，错误：{str(e)}")
                continue

        return f"企业批量入库完成，共成功导入 {import_count} 份私有文档"

    def clear_docs(self):
        """清空知识库（企业资料重置专用）"""
        kb.clear_store()
        return "企业知识库已清空，可重新导入新资料"

# 商用全局单例
batch_uploader = CommercialBatchUpload()
