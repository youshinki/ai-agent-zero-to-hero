# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 multi_tenant/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

def search(query, tenant_id):
    if not tenant_id:
        raise PermissionError("缺少租户标识")
    return vector_db.search(
        query, top_k=5,
        filter={"tenant_id": tenant_id}   # 硬过滤，不可被prompt绕过
    )
