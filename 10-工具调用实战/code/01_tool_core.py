import datetime
import ast

# ========== 工具定义列表（告诉模型有哪些工具可用）==========
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前系统日期和时间，当用户问现在几点、今天几号时使用",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_content",
            "description": "读取本地文本文件的内容，当用户要求查看、读取、分析某个文件时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要读取的文件路径，例如 ./docs/report.txt"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学表达式计算，当用户需要精确数值计算时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，例如 123.5 * 0.85 + 200"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# ========== 工具实际执行函数 ==========
def execute_tool(tool_name, tool_args):
    """根据工具名称和参数，真正执行对应功能"""

    if tool_name == "get_current_time":
        now = datetime.datetime.now()
        return f"当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')} 星期{['一','二','三','四','五','六','日'][now.weekday()]}"

    elif tool_name == "read_file_content":
        file_path = tool_args.get("file_path", "")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return f"文件内容（共{len(content)}字）：\n{content[:2000]}"
        except FileNotFoundError:
            return f"错误：找不到文件 {file_path}"
        except Exception as e:
            return f"读取文件出错：{str(e)}"

    elif tool_name == "calculate":
        expr = tool_args.get("expression", "")
        try:
            # 安全的数学计算（不执行任意代码）
            result = eval(expr, {"__builtins__": {}}, {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow
            })
            return f"计算结果：{expr} = {result}"
        except Exception as e:
            return f"计算出错：{str(e)}"

    else:
        return f"错误：未知工具 {tool_name}"
