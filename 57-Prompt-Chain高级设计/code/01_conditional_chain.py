# -*- coding: utf-8 -*-
# 条件链：便宜小模型做路由，业务分支才用主力大模型
def llm_fast(prompt: str) -> str:
    # 便宜的小模型（入口分类用），此处占位
    return "other"


def llm(prompt: str) -> str:
    # 主力大模型，此处占位
    return ""


def query_order(text: str) -> str:
    # 工具：查订单
    return ""


def query_policy(order: str) -> str:
    # 工具：查售后政策
    return ""


def route_by_intent(text):
    """用轻量模型判断意图，返回分支键"""
    prompt = f"""你是客服意图分类器。
    判断下面这条用户消息属于哪一类：
    - presale: 售前咨询、想买、问价格
    - after_sale: 售后、退换货、投诉
    - other: 其他
    只输出一个单词。
    消息：{text}"""
    result = llm_fast(prompt)   # 用便宜的小模型
    return result.strip().lower()


def presale_chain(text):
    return llm("你是产品推荐顾问，结合知识库推荐合适产品：" + text)


def aftersale_chain(text):
    order = query_order(text)          # 先插工具查订单
    policy = query_policy(order)       # 再查售后政策
    return llm(f"""订单信息：{order}；售后政策：{policy}。
    请给出处理结论。""")


def main_chain(text):
    intent = route_by_intent(text)     # 第一步：分类
    if intent == "presale":
        return presale_chain(text)     # 分支一
    elif intent == "after_sale":
        return aftersale_chain(text)   # 分支二
    return llm("请礼貌地引导用户到人工客服：" + text)
