# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 canary/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

NEW_VERSION_TENANTS = {"test_customer", "internal"}

def route_version(tenant_id, query):
    if tenant_id in NEW_VERSION_TENANTS:
        return run_v2(query)   # 灰度用户走新版
    return run_v1(query)       # 其他人走稳定旧版
