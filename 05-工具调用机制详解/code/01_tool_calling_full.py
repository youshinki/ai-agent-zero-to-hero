#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第5篇配套完整演示代码
工具调用机制详解：让AI Agent从"会说"到"会做"
==========================================================================

本文件为《AI Agent 零基础实战》第5篇的配套完整项目代码。
完全基于文章内容编写，覆盖文中全部技术点，使用模拟API，可直接运行。

运行方式: python 01_tool_calling_full.py
"""

import json
import math
import random
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


# ======================================================================
# 第一部分：工具定义系统 —— 遵循四大设计原则
# 原则1: 职责单一 - 每个工具只做一件事
# 原则2: 参数明确 - 类型、说明、必填、示例值
# 原则3: 结果结构化 - 返回JSON格式
# 原则4: 人机边界 - 高风险操作需确认
# ======================================================================

class Tool:
    """工具基类 - 遵循职责单一原则"""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters  # 参数定义（类型、说明、是否必填）
        self.requires_confirmation = False  # 是否需要人工确认（人机边界）
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具 - 子类覆盖此方法"""
        raise NotImplementedError
    
    def to_openai_format(self) -> Dict[str, Any]:
        """转为OpenAI Function Calling格式"""
        props = {}
        required = []
        for pname, pinfo in self.parameters.items():
            props[pname] = {
                "type": pinfo.get("type", "string"),
                "description": pinfo.get("description", ""),
            }
            if pinfo.get("required", False):
                required.append(pname)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": required,
                }
            }
        }


# ======================================================================
# 第二部分：五类工具的完整实现
# ======================================================================

# ----- 1. 信息查询工具（搜索引擎、天气查询、新闻检索） -----

class WebSearchTool(Tool):
    """搜索引擎工具 - 解决模型知识滞后问题"""
    def __init__(self):
        super().__init__(
            name="web_search",
            description="搜索互联网获取最新信息，适合查询实时数据、新闻、知识",
            parameters={
                "query": {
                    "type": "string",
                    "description": "搜索关键词，越精确越好",
                    "required": True,
                    "example": "2024年AI行业发展趋势"
                },
                "num_results": {
                    "type": "integer",
                    "description": "返回结果数量",
                    "required": False,
                    "default": 3
                }
            }
        )
    
    def execute(self, query: str = "", num_results: int = 3, **kwargs) -> Dict[str, Any]:
        # 模拟搜索
        mock_results = {
            "AI行业趋势": [
                {"title": "2024年AI Agent市场规模达100亿美元", "url": "https://example.com/1"},
                {"title": "多模态大模型成为行业新方向", "url": "https://example.com/2"},
                {"title": "RAG技术让企业知识库准确率提升至95%", "url": "https://example.com/3"},
            ],
            "天气": [
                {"title": "今日全国天气概况", "content": "北方晴暖，南方多雨"},
            ]
        }
        results = mock_results.get(query, [
            {"title": f"关于「{query}」的搜索结果1", "content": f"相关内容摘要..."},
            {"title": f"关于「{query}」的搜索结果2", "content": f"更多详细信息..."},
        ])[:num_results]
        return {"success": True, "results": results, "total": len(results)}


class WeatherTool(Tool):
    """天气查询工具"""
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="查询指定城市的实时天气信息",
            parameters={
                "city": {
                    "type": "string",
                    "description": "城市名称，如北京、上海、广州",
                    "required": True,
                    "example": "北京"
                }
            }
        )
    
    def execute(self, city: str = "", **kwargs) -> Dict[str, Any]:
        mock_weather = {
            "北京": {"temp": 22, "weather": "晴", "humidity": 45, "wind": "东南风3级", "aqi": 68},
            "上海": {"temp": 26, "weather": "多云", "humidity": 60, "wind": "南风2级", "aqi": 72},
            "广州": {"temp": 30, "weather": "阵雨", "humidity": 80, "wind": "西南风3级", "aqi": 55},
            "深圳": {"temp": 28, "weather": "晴", "humidity": 65, "wind": "东北风2级", "aqi": 48},
            "杭州": {"temp": 24, "weather": "阴", "humidity": 70, "wind": "东风2级", "aqi": 62},
        }
        w = mock_weather.get(city, {"temp": 25, "weather": "未知", "humidity": 50, "wind": "未知", "aqi": 50})
        return {"success": True, "city": city, **w}


class NewsTool(Tool):
    """新闻检索工具"""
    def __init__(self):
        super().__init__(
            name="get_news",
            description="检索最新新闻资讯",
            parameters={
                "category": {
                    "type": "string",
                    "description": "新闻类别: tech(科技), finance(财经), sports(体育)",
                    "required": False,
                    "default": "tech"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回条数",
                    "required": False,
                    "default": 5
                }
            }
        )
    
    def execute(self, category: str = "tech", limit: int = 5, **kwargs) -> Dict[str, Any]:
        news_db = {
            "tech": [
                "OpenAI发布GPT-5，推理能力大幅提升",
                "国内大模型厂商掀起价格战",
                "AI Agent开发框架LangChain发布2.0版本",
                "多模态AI在医疗影像诊断中取得突破",
                "自动驾驶L4级别在10个城市开放测试",
            ],
            "finance": [
                "央行宣布降准0.5个百分点",
                "A股三大指数全线上涨",
                "比特币价格突破10万美元大关",
                "新能源板块持续走强",
            ],
            "sports": [
                "中国队在亚运会再创佳绩",
                "NBA新赛季即将开打",
            ]
        }
        news = news_db.get(category, [])[:limit]
        return {"success": True, "category": category, "news": news, "count": len(news)}


# ----- 2. 文件处理工具（读文件、写文件） -----

class ReadFileTool(Tool):
    """文件读取工具"""
    def __init__(self):
        super().__init__(
            name="read_file",
            description="读取本地文件内容，支持txt、json、csv格式",
            parameters={
                "filepath": {
                    "type": "string",
                    "description": "文件路径",
                    "required": True,
                    "example": "./data/report.txt"
                },
                "encoding": {
                    "type": "string",
                    "description": "文件编码",
                    "required": False,
                    "default": "utf-8"
                }
            }
        )
    
    def execute(self, filepath: str = "", encoding: str = "utf-8", **kwargs) -> Dict[str, Any]:
        # 模拟文件读取
        mock_files = {
            "./data/report.txt": "2024年Q1销售报告\n总销售额：1,200,000元\n同比增长：15%\n完成率：108%",
            "./data/meeting_notes.txt": "会议主题：Q2产品规划\n参会人：张总、李经理、王工\n决议：5月启动新版本开发",
            "./data/customers.json": json.dumps([
                {"name": "张三", "level": "VIP", "spent": 50000},
                {"name": "李四", "level": "普通", "spent": 3000},
            ], ensure_ascii=False, indent=2),
        }
        content = mock_files.get(filepath, f"[模拟读取] 文件 {filepath} 的内容示例...")
        return {"success": True, "filepath": filepath, "content": content, "size": len(content)}


class WriteFileTool(Tool):
    """文件写入工具"""
    def __init__(self):
        super().__init__(
            name="write_file",
            description="写入内容到本地文件",
            parameters={
                "filepath": {
                    "type": "string",
                    "description": "目标文件路径",
                    "required": True,
                    "example": "./output/report.md"
                },
                "content": {
                    "type": "string",
                    "description": "要写入的文件内容",
                    "required": True,
                    "example": "# 报告标题\n\n正文内容..."
                }
            }
        )
        self.requires_confirmation = True  # 写入文件需确认
    
    def execute(self, filepath: str = "", content: str = "", **kwargs) -> Dict[str, Any]:
        return {"success": True, "filepath": filepath, "size": len(content), "message": f"文件已写入 {filepath}"}


# ----- 3. 代码与计算工具（计算器、Python执行器） -----

class CalculatorTool(Tool):
    """精确计算工具 - 解决模型不擅长精确计算的问题"""
    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算，支持加减乘除、幂运算、三角函数等",
            parameters={
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 (100+200)*0.3",
                    "required": True,
                    "example": "15000 * 0.15"
                }
            }
        )
    
    def execute(self, expression: str = "", **kwargs) -> Dict[str, Any]:
        # 安全计算
        allowed_chars = set("0123456789+-*/().%")
        safe = all(c in allowed_chars for c in expression)
        if not safe:
            return {"success": False, "error": "表达式包含非法字符"}
        try:
            result = eval(expression, {"__builtins__": {}}, {"math": math})
            return {"success": True, "expression": expression, "result": round(result, 4)}
        except Exception as e:
            return {"success": False, "expression": expression, "error": str(e)}


class DataAnalyzerTool(Tool):
    """数据分析工具"""
    def __init__(self):
        super().__init__(
            name="analyze_data",
            description="对数据进行统计分析，计算平均值、总和、最大值、最小值等",
            parameters={
                "data": {
                    "type": "array",
                    "description": "要分析的数值列表",
                    "required": True,
                    "example": [100, 200, 150, 300, 250]
                },
                "operations": {
                    "type": "array",
                    "description": "要执行的分析操作: sum, avg, max, min, count",
                    "required": False,
                    "example": ["sum", "avg", "max"]
                }
            }
        )
    
    def execute(self, data: List[float] = None, operations: List[str] = None, **kwargs) -> Dict[str, Any]:
        if data is None:
            data = []
        if operations is None:
            operations = ["sum", "avg", "count"]
        results = {}
        if "sum" in operations:
            results["sum"] = sum(data)
        if "avg" in operations:
            results["avg"] = round(sum(data) / len(data), 2) if data else 0
        if "max" in operations:
            results["max"] = max(data) if data else 0
        if "min" in operations:
            results["min"] = min(data) if data else 0
        if "count" in operations:
            results["count"] = len(data)
        return {"success": True, "data_size": len(data), "results": results}


# ----- 4. 业务系统工具（发送邮件、查询工单） -----

class SendEmailTool(Tool):
    """发送邮件工具"""
    def __init__(self):
        super().__init__(
            name="send_email",
            description="发送电子邮件给指定收件人",
            parameters={
                "to": {
                    "type": "string",
                    "description": "收件人邮箱",
                    "required": True,
                    "example": "user@example.com"
                },
                "subject": {
                    "type": "string",
                    "description": "邮件主题",
                    "required": True,
                    "example": "周报自动生成通知"
                },
                "body": {
                    "type": "string",
                    "description": "邮件正文内容",
                    "required": True,
                    "example": "本周工作周报已生成..."
                }
            }
        )
        self.requires_confirmation = True  # 发送邮件需人工确认（人机边界）
    
    def execute(self, to: str = "", subject: str = "", body: str = "", **kwargs) -> Dict[str, Any]:
        return {
            "success": True,
            "to": to,
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
            "message": f"邮件已发送至 {to}"
        }


class QueryOrderTool(Tool):
    """查询工单/订单工具"""
    def __init__(self):
        super().__init__(
            name="query_order",
            description="查询订单或工单的状态和信息",
            parameters={
                "order_id": {
                    "type": "string",
                    "description": "订单/工单编号",
                    "required": True,
                    "example": "ORD-2024-001"
                }
            }
        )
    
    def execute(self, order_id: str = "", **kwargs) -> Dict[str, Any]:
        mock_orders = {
            "ORD-2024-001": {"status": "已发货", "product": "AI智能客服系统", "amount": 50000, "date": "2024-01-15"},
            "ORD-2024-002": {"status": "处理中", "product": "私有知识库搭建", "amount": 30000, "date": "2024-01-20"},
            "TICKET-001": {"status": "进行中", "title": "知识库问答返回异常", "priority": "高", "assignee": "王工"},
        }
        order = mock_orders.get(order_id, {"status": "未找到", "error": f"订单 {order_id} 不存在"})
        return {"success": True, "order_id": order_id, **order}


# ----- 5. 视觉与多媒体工具（OCR描述、图片描述） -----

class OCRTool(Tool):
    """OCR文字识别工具"""
    def __init__(self):
        super().__init__(
            name="ocr_recognize",
            description="识别图片中的文字内容（OCR）",
            parameters={
                "image_path": {
                    "type": "string",
                    "description": "图片文件路径",
                    "required": True,
                    "example": "./images/invoice.jpg"
                },
                "language": {
                    "type": "string",
                    "description": "识别语言: chinese(中文), english(英文)",
                    "required": False,
                    "default": "chinese"
                }
            }
        )
    
    def execute(self, image_path: str = "", language: str = "chinese", **kwargs) -> Dict[str, Any]:
        # 模拟OCR识别
        mock_ocr = {
            "./images/invoice.jpg": "发票号码：12345678\n金额：¥5,000.00\n日期：2024-01-15\n开票方：XX科技有限公司",
            "./images/report.png": "2024年Q1销售数据\n总营收：120万\n同比增长15%",
        }
        text = mock_ocr.get(image_path, f"[模拟OCR识别] 从 {image_path} 中识别出文字内容示例...")
        return {"success": True, "text": text, "language": language, "chars": len(text)}


class ImageDescriptionTool(Tool):
    """图片描述工具"""
    def __init__(self):
        super().__init__(
            name="describe_image",
            description="生成图片的内容描述",
            parameters={
                "image_path": {
                    "type": "string",
                    "description": "图片文件路径",
                    "required": True,
                    "example": "./images/chart.png"
                },
                "detail_level": {
                    "type": "string",
                    "description": "描述详细程度: brief(简要), detailed(详细)",
                    "required": False,
                    "default": "detailed"
                }
            }
        )
    
    def execute(self, image_path: str = "", detail_level: str = "detailed", **kwargs) -> Dict[str, Any]:
        descriptions = {
            "./images/chart.png": "这是一张柱状图，展示了2024年Q1各月销售数据：1月35万，2月40万，3月45万，呈稳步上升趋势。",
            "./images/logo.png": "一个蓝色调的科技公司Logo，包含AI字母组合，风格现代简洁。",
        }
        desc = descriptions.get(image_path, f"[模拟图片描述] 对 {image_path} 的视觉内容描述...")
        return {"success": True, "description": desc, "detail_level": detail_level}


# ======================================================================
# 第三部分：工具注册管理器
# ======================================================================

class ToolRegistry:
    """工具注册中心 - 管理所有可用工具"""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._call_history: List[Dict] = []  # 调用历史（与记忆模块协同）
    
    def register(self, tool: Tool):
        """注册一个工具"""
        self._tools[tool.name] = tool
    
    def register_defaults(self):
        """注册所有默认工具"""
        tools = [
            WebSearchTool(), WeatherTool(), NewsTool(),
            ReadFileTool(), WriteFileTool(),
            CalculatorTool(), DataAnalyzerTool(),
            SendEmailTool(), QueryOrderTool(),
            OCRTool(), ImageDescriptionTool(),
        ]
        for t in tools:
            self.register(t)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        return [{"name": t.name, "description": t.description}
                for t in self._tools.values()]
    
    def get_tool_definitions(self) -> List[Dict]:
        """获取所有工具的OpenAI Function Calling格式定义"""
        return [t.to_openai_format() for t in self._tools.values()]
    
    def execute_tool(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用 —— 核心方法"""
        tool = self.get_tool(name)
        if not tool:
            return {"success": False, "error": f"工具 '{name}' 不存在"}
        
        # 人机边界检查
        if tool.requires_confirmation:
            # 模拟人工确认（实际项目需要交互）
            pass
        
        # 执行工具
        result = tool.execute(**params)
        
        # 记录调用历史（与记忆模块协同）
        self._call_history.append({
            "tool": name,
            "params": params,
            "result": result,
            "time": datetime.now().isoformat()
        })
        
        return result
    
    def get_call_history(self) -> List[Dict]:
        """获取工具调用历史 —— 与记忆模块协同"""
        return self._call_history[-10:]  # 最近10条


# ======================================================================
# 第四部分：模拟LLM决策引擎
# ======================================================================

class MockLLM:
    """模拟大模型调用 - 根据输入决定是否调用工具及调用哪个工具"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    def decide_tool_call(self, user_input: str) -> Dict[str, Any]:
        """模拟模型判断：是否需要调用工具？调用哪个？参数是什么？"""
        input_lower = user_input.lower()
        
        # 天气查询
        if any(kw in input_lower for kw in ["天气", "气温", "温度", "下雨"]):
            cities = ["北京", "上海", "广州", "深圳", "杭州", "武汉", "成都", "南京"]
            city = next((c for c in cities if c in user_input), "北京")
            return {"needs_tool": True, "tool": "get_weather", "params": {"city": city}}
        
        # 搜索
        if any(kw in input_lower for kw in ["搜索", "查找", "查一下", "最新", "新闻", "消息"]):
            return {"needs_tool": True, "tool": "web_search", "params": {"query": user_input.replace("搜索", "").strip(), "num_results": 3}}
        
        # 计算
        if any(kw in input_lower for kw in ["计算", "多少钱", "多少", "加", "减", "乘", "除", "百分比"]):
            return {"needs_tool": True, "tool": "calculator", "params": {"expression": "15000 * 0.15"}}
        
        # 数据分析
        if any(kw in input_lower for kw in ["分析", "统计", "平均值", "总和", "最大"]):
            return {"needs_tool": True, "tool": "analyze_data", "params": {"data": [100, 200, 150, 300, 250, 180], "operations": ["sum", "avg", "max", "min", "count"]}}
        
        # 读文件
        if any(kw in input_lower for kw in ["读取", "打开文件", "看文件", "读文件"]):
            return {"needs_tool": True, "tool": "read_file", "params": {"filepath": "./data/report.txt"}}
        
        # 写文件
        if any(kw in input_lower for kw in ["保存", "写入", "写文件"]):
            return {"needs_tool": True, "tool": "write_file", "params": {"filepath": "./output/result.md", "content": "# 结果\n\n自动生成的内容"}}
        
        # OCR
        if any(kw in input_lower for kw in ["识别", "ocr", "图片文字"]):
            return {"needs_tool": True, "tool": "ocr_recognize", "params": {"image_path": "./images/invoice.jpg"}}
        
        # 发邮件
        if any(kw in input_lower for kw in ["发邮件", "发送邮件", "邮件通知"]):
            return {"needs_tool": True, "tool": "send_email", "params": {"to": "user@example.com", "subject": "自动通知", "body": f"关于：{user_input}"}}
        
        # 查订单
        if any(kw in input_lower for kw in ["订单", "工单", "查询订单"]):
            return {"needs_tool": True, "tool": "query_order", "params": {"order_id": "ORD-2024-001"}}
        
        # 不需要工具
        return {"needs_tool": False, "tool": None, "params": {}}
    
    def generate_response(self, user_input: str, tool_result: Optional[Dict] = None) -> str:
        """模拟模型生成最终回答"""
        if tool_result and tool_result.get("success"):
            # 查询天气
            if "city" in tool_result and "temp" in tool_result:
                w = tool_result
                return f"{w['city']}今天天气：{w['weather']}，{w['temp']}℃，湿度{w['humidity']}%，{w['wind']}，空气质量指数{w['aqi']}。{'适合户外活动！' if w['aqi'] < 70 else '建议减少户外活动。'}"
            # 搜索
            if "results" in tool_result:
                items = tool_result["results"]
                result_str = "\n".join([f"• {r['title']}" for r in items])
                return f"搜索到以下结果：\n{result_str}"
            # 计算
            if "result" in tool_result:
                return f"计算结果：{user_input} = {tool_result['result']}"
            # 数据分析
            if "results" in tool_result:
                r = tool_result["results"]
                return f"数据分析结果：\n总和={r.get('sum')}，平均值={r.get('avg')}，最大值={r.get('max')}，最小值={r.get('min')}，共{r.get('count')}条数据"
            # 其他成功结果
            return f"操作成功完成。"
        else:
            return f"关于「{user_input}」的回答：这是一个普通对话问题，不需要调用工具。"


# ======================================================================
# 第五部分：完整Agent（工具调用6步链路 + 与规划/记忆/反思协同）
# ======================================================================

class ToolCallingAgent:
    """完整的工具调用Agent
    
    实现工具调用6步链路：
    1. 接收任务
    2. 判断是否需要工具
    3. 选择工具并生成参数
    4. 代码执行工具
    5. 返回观察结果
    6. 生成最终回答
    """
    
    def __init__(self):
        self.registry = ToolRegistry()
        self.registry.register_defaults()
        self.llm = MockLLM(self.registry)
        self.conversation_history: List[Dict] = []  # 与记忆模块协同
    
    def run(self, user_input: str, verbose: bool = True) -> str:
        """执行一次工具调用完整流程"""
        if verbose:
            print(f"\n{'='*60}")
            print(f"📥 第1步：接收任务")
            print(f"用户输入：{user_input}")
        
        # ---- 第2步：判断是否需要工具 ----
        if verbose:
            print(f"\n🧠 第2步：判断是否需要工具")
        
        decision = self.llm.decide_tool_call(user_input)
        
        if not decision["needs_tool"]:
            if verbose:
                print(f"判断结果：不需要工具，直接回答")
            response = self.llm.generate_response(user_input)
            if verbose:
                print(f"\n📤 最终回答：{response}")
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        # ---- 第3步：选择工具并生成参数 ----
        tool_name = decision["tool"]
        params = decision["params"]
        if verbose:
            print(f"判断结果：需要调用工具")
            print(f"\n🔧 第3步：选择工具并生成参数")
            print(f"选择工具：{tool_name}")
            print(f"生成参数：{json.dumps(params, ensure_ascii=False)}")
        
        # ---- 第4步：代码执行工具 ----
        if verbose:
            print(f"\n⚙️ 第4步：代码执行工具")
        
        tool_result = self.registry.execute_tool(tool_name, params)
        
        if verbose:
            print(f"工具执行结果：{json.dumps(tool_result, ensure_ascii=False, indent=2)}")
        
        # ---- 第5步：返回观察结果 ----
        if verbose:
            print(f"\n👁️ 第5步：返回观察结果给模型")
        
        # ---- 第6步：生成最终回答 ----
        if verbose:
            print(f"\n📝 第6步：模型基于工具结果生成最终回答")
        
        response = self.llm.generate_response(user_input, tool_result)
        
        if verbose:
            print(f"\n📤 最终回答：{response}")
        
        self.conversation_history.append({"role": "user", "content": user_input, "tool_call": {"tool": tool_name, "params": params, "result": tool_result}})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def run_with_planning(self, complex_task: str, verbose: bool = True) -> str:
        """与规划模块协同的复杂任务执行"""
        if verbose:
            print(f"\n{'='*60}")
            print(f"🔄 工具调用 + 规划模块协同")
            print(f"复杂任务：{complex_task}")
        
        # 规划模块拆解任务
        if verbose:
            print(f"\n📋 [规划模块] 拆解任务：")
        
        steps = [
            {"step": 1, "name": "搜索最新数据", "tool": "web_search"},
            {"step": 2, "name": "分析数据统计", "tool": "analyze_data"},
            {"step": 3, "name": "保存分析报告", "tool": "write_file"},
            {"step": 4, "name": "发送报告邮件", "tool": "send_email"},
        ]
        
        for s in steps:
            print(f"  步骤{s['step']}：{s['name']}（工具：{s['tool']}）")
        
        # 执行每个步骤
        results = []
        for s in steps:
            if verbose:
                print(f"\n  ▶ 执行步骤{s['step']}：{s['name']}")
            
            if s['tool'] == 'web_search':
                r = self.registry.execute_tool('web_search', {"query": "2024年AI行业趋势", "num_results": 3})
            elif s['tool'] == 'analyze_data':
                r = self.registry.execute_tool('analyze_data', {"data": [120, 150, 180, 200, 250], "operations": ["sum", "avg", "max"]})
            elif s['tool'] == 'write_file':
                r = self.registry.execute_tool('write_file', {"filepath": "./output/analysis_report.md", "content": "# AI行业趋势分析报告\n\n## 核心发现\n..."})
            elif s['tool'] == 'send_email':
                r = self.registry.execute_tool('send_email', {"to": "boss@company.com", "subject": "AI行业趋势报告", "body": "报告已生成，请查收附件。"})
            else:
                r = {"success": False}
            
            results.append({"step": s['step'], "result": r})
            if verbose:
                print(f"  完成：{r.get('message', '操作成功')}")
        
        # 汇总结果
        summary = "计划执行完成！已依次完成：搜索数据→分析统计→保存报告→发送邮件。"
        if verbose:
            print(f"\n✅ 最终汇总：{summary}")
        return summary


# ======================================================================
# 第六部分：主程序 - 演示所有功能
# ======================================================================

def demo_single_tool_calls():
    """演示单个工具调用 - 6步链路"""
    print("\n" + "="*70)
    print("          🛠️ 工具调用完整6步链路演示")
    print("="*70)
    
    agent = ToolCallingAgent()
    
    test_cases = [
        "今天上海天气怎么样？",
        "搜索2024年AI Agent行业趋势",
        "计算15000乘以0.15",
        "帮我分析这组数据：100, 200, 150, 300, 250, 180",
        "读取报告文件",
        "帮我看看订单ORD-2024-001",
    ]
    
    for case in test_cases:
        agent.run(case, verbose=True)


def demo_all_tool_types():
    """演示五类工具"""
    print("\n" + "="*70)
    print("          📦 五类工具完整演示")
    print("="*70)
    
    registry = ToolRegistry()
    registry.register_defaults()
    
    # 1. 信息查询工具
    print("\n--- 1. 信息查询工具 ---")
    r1 = registry.execute_tool("web_search", {"query": "AI行业趋势"})
    print(f"  搜索：找到 {r1['total']} 条结果")
    
    r2 = registry.execute_tool("get_weather", {"city": "深圳"})
    print(f"  天气：深圳 {r2['weather']} {r2['temp']}℃")
    
    r3 = registry.execute_tool("get_news", {"category": "tech", "limit": 3})
    print(f"  新闻：获取 {r3['count']} 条科技资讯")
    
    # 2. 文件处理工具
    print("\n--- 2. 文件处理工具 ---")
    r4 = registry.execute_tool("read_file", {"filepath": "./data/report.txt"})
    print(f"  读取：{r4['content'][:50]}...")
    
    r5 = registry.execute_tool("write_file", {"filepath": "./output/test.md", "content": "test"})
    print(f"  写入：{r5['message']}")
    
    # 3. 代码与计算工具
    print("\n--- 3. 代码与计算工具 ---")
    r6 = registry.execute_tool("calculator", {"expression": "(1000+2000)*0.3"})
    print(f"  计算：{r6['expression']} = {r6['result']}")
    
    r7 = registry.execute_tool("analyze_data", {"data": [85, 92, 78, 95, 88], "operations": ["sum", "avg", "max", "min"]})
    print(f"  分析：sum={r7['results']['sum']}, avg={r7['results']['avg']}")
    
    # 4. 业务系统工具
    print("\n--- 4. 业务系统工具 ---")
    r8 = registry.execute_tool("send_email", {"to": "user@test.com", "subject": "测试", "body": "这是一封测试邮件"})
    print(f"  邮件：{r8['message']}")
    
    r9 = registry.execute_tool("query_order", {"order_id": "ORD-2024-001"})
    print(f"  订单：{r9['status']} - {r9['product']}")
    
    # 5. 视觉与多媒体工具
    print("\n--- 5. 视觉与多媒体工具 ---")
    r10 = registry.execute_tool("ocr_recognize", {"image_path": "./images/invoice.jpg"})
    print(f"  OCR：{r10['text'][:50]}...")
    
    r11 = registry.execute_tool("describe_image", {"image_path": "./images/chart.png", "detail_level": "brief"})
    print(f"  图片描述：{r11['description'][:60]}...")
    
    # 调用历史（与记忆模块协同）
    print(f"\n--- 调用历史（与记忆模块协同）---")
    history = registry.get_call_history()
    print(f"  已记录 {len(history)} 次工具调用")


def demo_tool_design_principles():
    """演示四大设计原则"""
    print("\n" + "="*70)
    print("          📐 四大设计原则演示")
    print("="*70)
    
    # 原则1：职责单一
    print("\n原则1️⃣ 职责单一：每个工具只做一件事")
    print("  web_search: 只搜索信息")
    print("  get_weather: 只查天气")
    print("  calculator: 只做计算")
    print("  绝不出现一个工具既查天气又发邮件")
    
    # 原则2：参数明确
    print("\n原则2️⃣ 参数定义明确")
    tool = WeatherTool()
    fmt = tool.to_openai_format()
    params = fmt["function"]["parameters"]["properties"]
    for pname, pinfo in params.items():
        print(f"  {pname}: type={pinfo['type']}, desc={pinfo['description']}")
    
    # 原则3：结果结构化
    print("\n原则3️⃣ 结果格式结构化（JSON）")
    r = registry = ToolRegistry()
    registry.register_defaults()
    result = registry.execute_tool("get_weather", {"city": "北京"})
    print(f"  返回类型: {type(result).__name__}")
    print(f"  包含字段: {', '.join(result.keys())}")
    
    # 原则4：人机边界
    print("\n原则4️⃣ 人机边界（高风险操作需确认）")
    send_email = SendEmailTool()
    write_file = WriteFileTool()
    print(f"  send_email.requires_confirmation = {send_email.requires_confirmation}")
    print(f"  write_file.requires_confirmation = {write_file.requires_confirmation}")
    print(f"  涉及发送/删除/修改的操作应有：人工确认、权限校验、风险提示、操作审计")


def demo_agent_collaboration():
    """演示工具与规划/记忆/反思的协同"""
    print("\n" + "="*70)
    print("          🔄 工具与Agent组件协同演示")
    print("="*70)
    
    agent = ToolCallingAgent()
    
    # 1. 与规划协同
    print("\n--- 与规划模块协同 ---")
    print("  规划模块：搜索资料 → 整理结果 → 生成报告")
    print("  工具系统：web_search → analyze_data → write_file")
    
    # 2. 与记忆协同
    print("\n--- 与记忆模块协同 ---")
    registry = ToolRegistry()
    registry.register_defaults()
    registry.execute_tool("get_weather", {"city": "北京"})
    registry.execute_tool("get_weather", {"city": "上海"})
    history = registry.get_call_history()
    print(f"  记忆模块记录了 {len(history)} 次工具调用历史")
    print(f"  最近调用：{history[-1]['tool']}")
    
    # 3. 与反思协同
    print("\n--- 与反思模块协同 ---")
    print("  反思模块检查：")
    print("  ✅ 参数是否正确（city=北京 ✓）")
    print("  ✅ 结果是否满足需求（天气数据完整 ✓）")
    print("  ✅ 是否需要二次调用（不需要 ✓）")
    print("  ✅ 是否存在冗余步骤（无冗余 ✓）")


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       🛠️ 工具调用机制详解 - 完整配套演示代码                ║
║       《AI Agent 零基础实战》第5篇                          ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    while True:
        print("\n" + "─" * 60)
        print("请选择演示模式：")
        print("1. 单次工具调用6步链路演示（包含多种场景）")
        print("2. 五类工具完整展示（信息查询/文件/计算/业务/多媒体）")
        print("3. 四大设计原则演示（职责单一/参数明确/结构化/人机边界）")
        print("4. 工具与Agent组件协同（规划/记忆/反思）")
        print("5. 全部运行")
        print("0. 退出")
        print("─" * 60)
        
        choice = input("请输入选项 (0-5): ").strip()
        
        if choice == "1":
            demo_single_tool_calls()
        elif choice == "2":
            demo_all_tool_types()
        elif choice == "3":
            demo_tool_design_principles()
        elif choice == "4":
            demo_agent_collaboration()
        elif choice == "5":
            demo_single_tool_calls()
            demo_all_tool_types()
            demo_tool_design_principles()
            demo_agent_collaboration()
        elif choice == "0":
            print("感谢使用！")
            break
        else:
            print("无效输入，请重新选择。")


if __name__ == "__main__":
    main()
