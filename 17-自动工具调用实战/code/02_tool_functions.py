# ===== 工具函数集：read_file 等 =====

def read_file(path: str) -> str:
    """读取本地文件内容"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"读取文件失败：{str(e)}"

def write_file(path: str, content: str) -> str:
    """写入内容到本地文件"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"文件写入成功"
    except Exception as e:
        return f"写入文件失败：{str(e)}"

def calculator(expression: str) -> str:
    """计算数学表达式，支持加减乘除和括号"""
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"计算失败：{str(e)}"

def create_default_tools():
    """创建默认工具集"""
    tool_manager = ToolManager()

    tool_manager.register_tool(
        name="read_file",
        description="读取本地文件内容，适合获取文档、代码、日志等信息",
        parameters={
            "path": "文件路径，字符串类型"
        },
        func=read_file
    )

    tool_manager.register_tool(
        name="write_file",
        description="将内容写入本地文件，适合保存结果、生成报告、记录数据",
        parameters={
            "path": "文件路径，字符串类型",
            "content": "要写入的内容，字符串类型"
        },
        func=write_file
    )

    tool_manager.register_tool(
        name="calculator",
        description="计算数学表达式，支持加减乘除和括号",
        parameters={
            "expression": "数学表达式，字符串类型，例如 '12+34'、'(100-20)*5'"
        },
        func=calculator
    )

    return tool_manager
