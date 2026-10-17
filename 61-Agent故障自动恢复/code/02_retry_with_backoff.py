# -*- coding: utf-8 -*-
# 指数退避重试：只重试可恢复故障，最多 3 次
import time

from tool_error import ToolError  # 见 01_tool_error.py


def retry_with_backoff(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except ToolError as e:
            if not e.retryable or attempt == max_retries - 1:
                raise e
            delay = base_delay * (2 ** attempt)   # 1s, 2s, 4s
            time.sleep(delay)
    raise ToolError("EXCEEDED", "重试次数用尽", retryable=False)
