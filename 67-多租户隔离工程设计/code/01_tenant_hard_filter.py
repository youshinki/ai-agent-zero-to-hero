def search(query, tenant_id):
    if not tenant_id:
        raise PermissionError("缺少租户标识")
    return vector_db.search(
        query, top_k=5,
        filter={"tenant_id": tenant_id}   # 硬过滤，不可被prompt绕过
    )
