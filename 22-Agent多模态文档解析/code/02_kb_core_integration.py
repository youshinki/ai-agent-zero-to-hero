# ===== kb_core.py：顶部新增导入 =====

# 顶部新增
from .parse_doc import parse_file_to_text

# ===== 替换 open 读取方式 =====

# 替换原来的 open 读取方式
# 原代码废弃：
# with open(file_path, "r", encoding="utf-8") as f:
#     content = f.read()

# 新的通用解析代码
content = parse_file_to_text(file_path)
if content.startswith("文档解析失败") or content.startswith("暂不支持解析"):
    return f"【解析失败】{os.path.basename(file_path)}：{content}"

# ===== 替换后缀判断逻辑 =====

# 替换原有后缀判断
# 原代码：if fname.endswith((".txt", ".md")):

# 新代码
if fname.endswith((".txt", ".md", ".pdf", ".docx")):
