# ===== kb_core.py：参考文献自动去重规整 =====

def get_ref_summary(self, ref_text: str) -> str:
    """
    提取并规整参考文献，自动去重、排序
    """
    if "来源文档：" not in ref_text:
        return ""

    lines = ref_text.split("\n")
    source_set = set()
    for line in lines:
        if "来源文档：" in line:
            source = line.split("来源文档：")[-1].strip()
            source_set.add(source)

    if not source_set:
        return ""

    ref_out = "\n\n【参考文献】\n"
    for idx, src in enumerate(list(source_set)):
        ref_out += f"{idx+1}. {src}\n"
    return ref_out
