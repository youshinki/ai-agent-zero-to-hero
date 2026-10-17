NEW_VERSION_TENANTS = {"test_customer", "internal"}

def route_version(tenant_id, query):
    if tenant_id in NEW_VERSION_TENANTS:
        return run_v2(query)   # 灰度用户走新版
    return run_v1(query)       # 其他人走稳定旧版
