# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 agent_private_kb/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

# ===== tools/tool_manager.py：知识库三大工具 =====

# 在文件顶部新增导入
from knowledge_base.kb_core import kb

# ---------- 新增知识库工具函数 ----------
def kb_upload_doc(file_path: str) -> str:
    """上传本地文档到私有知识库，完成切片与向量化入库"""
    return kb.add_doc_file(file_path)

def kb_search_query(query: str) -> str:
    """基于私有知识库进行语义检索，获取精准私有资料"""
    res_list = kb.search(query, top_k=3)
    if isinstance(res_list, str):
        return res_list
    out = "知识库检索结果：\n"
    for idx, item in enumerate(res_list):
        out += f"\n【片段{idx+1}】来源：{item['source']}\n内容：{item['content']}\n"
    return out

def kb_clear() -> str:
    """清空私有知识库所有数据"""
    return kb.clear_kb()

# ---------- 在 create_default_tools 函数中注册工具 ----------
def create_default_tools():
    tool_manager = ToolManager()

    # 原有工具不变...

    # 新增知识库工具注册
    tool_manager.register_tool(
        name="kb_upload_doc",
        description="将本地TXT、MD文档上传到私有知识库，完成切片和向量化入库，用于后续私有资料问答",
        parameters={"file_path": "本地文档文件路径，字符串格式"},
        func=kb_upload_doc
    )

    tool_manager.register_tool(
        name="kb_search_query",
        description="在私有知识库中进行语义检索，查询私有文档内容，回答私人、项目、自定义资料问题",
        parameters={"query": "用户提问或检索关键词"},
        func=kb_search_query
    )

    tool_manager.register_tool(
        name="kb_clear",
        description="清空私有知识库所有存储的文档与向量数据",
        parameters={},
        func=kb_clear
    )

    return tool_manager
