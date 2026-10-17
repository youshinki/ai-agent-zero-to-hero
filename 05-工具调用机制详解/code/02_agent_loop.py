# ---- 片段：工具执行与Agent工具调用主循环（block 7）----
def execute_tool(tool_name, parameters):
    if tool_name == "web_search":
        return search_web(parameters["query"])

# ---- 片段：工具执行与Agent工具调用主循环（block 8）----
def agent_run(user_input):
    # 1. 模型判断是否调用工具
    decision = llm_decide_tool(user_input, tools)

    if decision["use_tool"]:
        # 2. 执行工具
        result = execute_tool(
            decision["tool_name"],
            decision["parameters"]
        )

        # 3. 把结果交给模型继续处理
        return llm_generate(user_input, result)
    else:
        # 4. 不需要工具，直接回答
        return llm_direct_reply(user_input)

# ---- 片段：工具执行与Agent工具调用主循环（block 9）----
agent_run("今天上海天气怎么样？")
