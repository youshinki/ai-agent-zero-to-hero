# -*- coding: utf-8 -*-
# 参数校验三层防线：schema 声明 + 函数内格式校验 + 业务存在性校验
import re


def call_get_order(order_id: str):
    # 1. 格式校验：订单号必须是固定格式
    if not re.match(r"^ORD-\d{8}$", order_id):
        return {"error": "订单号格式错误，请用户提供正确的订单号"}
    # 2. 存在性校验
    order = db.query_order(order_id)  # noqa: F821（占位：数据库句柄）
    if order is None:
        return {"error": "未找到该订单，请确认订单号"}
    return order


# 工具注册时，参数 schema 也要写清楚
TOOL_SCHEMAS = [{
    "name": "get_order_status",
    "description": "查询订单物流状态。仅当用户提供了ORD-开头的订单号时调用。",
    "parameters": {
        "order_id": {"type": "string", "description": "格式为ORD-+8位数字，例如ORD-20240815"}
    }
}]
