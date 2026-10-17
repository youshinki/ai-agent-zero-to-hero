# ===== memory_utils.py：历史压缩 =====

from openai import OpenAI
from config import MODEL_API_KEY, MODEL_BASE_URL, MODEL_NAME
client = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)

COMPRESS_THRESHOLD = 20  # 超过20轮自动触发压缩
KEEP_RECENT = 10         # 保留最近10轮完整对话

def count_message_tokens(msg_list):
    total = 0
    for item in msg_list:
        total += len(item.get("content", ""))
    return total

def compress_history(history_list):
    """智能压缩：保留近期完整，将更早对话压缩为摘要"""
    if len(history_list) < COMPRESS_THRESHOLD:
        return history_list
    old_history = history_list[:-KEEP_RECENT]
    recent_history = history_list[-KEEP_RECENT:]
    concat_text = ""
    for item in old_history:
        role = "用户" if item["role"] == "user" else "AI"
        concat_text += f"{role}：{item['content']}\n"
    prompt = f"""
请对以下历史对话进行极致精简摘要：
1. 保留用户核心身份、需求、设定、关键结论
2. 删除客套话、重复话、冗余对话
3. 输出结构化总结，方便后续AI接续对话
4. 尽量短、信息密度最高
历史对话：
{concat_text}
    """
    res = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role":"user", "content":prompt}]
    )
    summary = res.choices[0].message.content
    compressed_item = {"role":"system",
        "content": f"【历史对话摘要】{summary}"}
    new_history = [compressed_item] + recent_history
    return new_history

# ===== config.py：压缩阈值常量 =====

COMPRESS_THRESHOLD = 20   # 触发压缩轮次
KEEP_RECENT = 10          # 保留最新完整轮次
