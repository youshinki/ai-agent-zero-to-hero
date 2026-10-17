# ===== kb_core.py：新增导入 =====

from .context_compressor import compressor

# ===== 全局 Token 适配参数 =====

# 上下文压缩Token阈值（可根据模型自由调整）
MAX_CONTEXT_TOKEN = 1800  # 适配绝大多数轻量模型

# ===== search 方法末尾新增压缩逻辑 =====

# 替换原有return输出
# 原有格式化输出代码保留，最后增加压缩处理
out = "【高精度知识库检索结果】\n"
for idx, item in enumerate(final_results):
    out += f"\n片段{idx+1}（综合匹配分：{item['total_score']}）\n"
    out += f"来源文档：{item['source']}\n"
    out += f"核心内容：{item['content']}\n"

# 新增：自适应上下文压缩，解决Token溢出
out = compressor.compress(out, MAX_CONTEXT_TOKEN)
return out
