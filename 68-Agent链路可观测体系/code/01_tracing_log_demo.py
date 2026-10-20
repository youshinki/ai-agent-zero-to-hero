# 【片段说明】本文件为文章正文代码摘录，依赖文中前文定义的变量/函数，
# 单独运行会报 NameError。可直接运行的完整项目见同目录 observability/ 包
#（含 README、config、测试，USE_MOCK=true 时无需 API 密钥）。

import uuid, time

def run_agent(query, session_id, tenant_id):
    trace_id = uuid.uuid4().hex[:12]
    log.info("request_start", trace_id=trace_id,
             tenant_id=tenant_id, session_id=session_id, query=query)

    t0 = time.time()
    docs = retrieve(query)
    log.info("retrieve_done", trace_id=trace_id,
             n_docs=len(docs), ms=int((time.time()-t0)*1000))

    tool_result = call_tool(...)
    log.info("tool_done", trace_id=trace_id, tool="get_order")

    answer = llm_generate(query, docs, tool_result)
    log.info("request_end", trace_id=trace_id,
             tokens=count_tokens(answer))
    return answer
