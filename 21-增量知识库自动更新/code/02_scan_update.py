# ===== 工具函数 kb_scan_update =====

# 新增工具函数
def kb_scan_update() -> str:
    """全自动扫描所有文档，增量更新知识库，无需手动上传"""
    log = kb.scan_all_update()
    return "知识库全自动增量更新完成：\n" + "\n".join(log)

def kb_increment_file(file_path: str) -> str:
    """针对单个文件增量更新，仅更新变动内容"""
    return kb.single_file_increment_update(file_path)

# 在 create_default_tools 中注册
tool_manager.register_tool(
    name="kb_scan_update",
    description="全自动扫描知识库文档目录，检测文件变动，执行增量更新，自动维护私有知识库",
    parameters={},
    func=kb_scan_update
)

tool_manager.register_tool(
    name="kb_increment_file",
    description="对指定单个文档执行增量更新，只更新修改部分，不重复计算全量内容",
    parameters={"file_path": "文档完整路径"},
    func=kb_increment_file
)

# ===== main.py：/api/kb/scan-update 接口 =====

@app.post("/api/kb/scan-update")
async def api_kb_scan_update():
    """一键全目录增量更新"""
    log = kb.scan_all_update()
    return {"code": 200, "log": log}

@app.post("/api/kb/increment-file")
async def api_increment_file(file_path: str):
    """单文件增量更新"""
    res = kb.single_file_increment_update(file_path)
    return {"code": 200, "msg": res}
