# -*- coding: utf-8 -*-
# 结构化错误：每个错误打 retryable 标签，而不是裸抛异常
import requests


class ToolError(Exception):
    def __init__(self, code, message, retryable):
        self.code = code          # TIMEOUT / PARAM_ERROR / AUTH_FAIL / NOT_FOUND
        self.message = message
        self.retryable = retryable
        super().__init__(message)


def call_order_api(order_id):
    try:
        resp = requests.get(f"https://api.xxx/order/{order_id}", timeout=5)
        if resp.status_code == 429:
            raise ToolError("RATE_LIMIT", "接口限流，请稍后重试", retryable=True)
        if resp.status_code == 404:
            raise ToolError("NOT_FOUND", "订单不存在", retryable=False)
        if resp.status_code >= 500:
            raise ToolError("SERVER_ERROR", "订单服务内部错误", retryable=True)
        return resp.json()
    except requests.Timeout:
        raise ToolError("TIMEOUT", "订单查询超时", retryable=True)
