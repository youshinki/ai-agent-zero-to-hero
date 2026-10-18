# 第53篇配套代码：ReAct模式深度剖析
# 推理与行动循环底层机制的完整实现
# 运行：python 01_react_full_implementation.py

import json
import re

# ========== ReAct Prompt模板（带可用工具定义） ==========
REACT_PROMPT_TEMPLATE = """你是一个智能助手，擅长通过思考和调用工具来解决问题。

## 可用工具
1. search(query: str) - 搜索网络获取实时信息
2. calculator(expression: str) - 数学计算
3. get_weather(city: str) - 查询城市天气
4. get_time() - 获取当前时间

## 输出格式
每一轮必须按以下格式回答：
Thought: <你现在的思考过程>
Action: <工具名> | <参数>

当信息足够回答问题时，直接输出：
Final Answer: <最终答案>

## 历史记录
{history}

## 当前问题
{question}
"""

# ========== 可用的工具 ==========
class Tools:
    """ReAct可用工具集"""
    
    @staticmethod
    def search(query):
        return f"[搜索结果] 关于'{query}'的最新信息：找到了3条相关结果"
    
    @staticmethod
    def calculator(expression):
        try:
            return f"[计算结果] {expression} = {eval(expression)}"
        except:
            return f"[错误] 表达式'{expression}'无效"
    
    @staticmethod
    def get_weather(city):
        weather_data = {
            "北京": {"temp": 22, "weather": "晴", "humidity": 45},
            "上海": {"temp": 26, "weather": "多云", "humidity": 60},
            "广州": {"temp": 30, "weather": "阵雨", "humidity": 80},
            "深圳": {"temp": 28, "weather": "晴", "humidity": 65}
        }
        w = weather_data.get(city, {"temp": 25, "weather": "未知", "humidity": 50})
        return f"[天气] {city}：{w['weather']}，{w['temp']}℃，湿度{w['humidity']}%"
    
    @staticmethod
    def get_time():
        from datetime import datetime
        return f"[时间] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    TOOL_MAP = {
        "search": search,
        "calculator": calculator,
        "get_weather": get_weather,
        "get_time": get_time
    }

# ========== ReAct Agent完整实现 ==========
class ReActAgent:
    """完整的ReAct模式实现"""
    
    def __init__(self):
        self.history = []
        self.max_steps = 10
    
    def _parse_action(self, output):
        """解析模型的Action输出"""
        # 匹配 Final Answer
        if "Final Answer:" in output:
            return {"type": "final", "content": output.split("Final Answer:")[-1].strip()}
        
        # 匹配 Action
        action_match = re.search(r'Action:\s*(\w+)\s*\|\s*(.+)', output)
        if action_match:
            return {
                "type": "action",
                "tool": action_match.group(1).strip(),
                "params": action_match.group(2).strip()
            }
        
        # 匹配 Thought
        thought_match = re.search(r'Thought:\s*(.+)', output)
        if thought_match:
            return {"type": "thought", "content": thought_match.group(1).strip()}
        
        return {"type": "unknown", "content": output}
    
    def _call_llm(self, prompt):
        """模拟LLM调用（实际使用替换为真实API）"""
        # 模拟ReAct推理过程
        if "search" in prompt:
            return f"Thought: 我需要搜索相关信息来回答问题。\nAction: search | {prompt[:30]}"
        elif "天气" in prompt or "weather" in prompt:
            return f"Thought: 查询城市天气信息。\nAction: get_weather | 北京"
        elif "计算" in prompt or "calculate" in prompt:
            return f"Thought: 我需要用计算器算一下。\nAction: calculator | 100 + 200"
        else:
            return f"Final Answer: 根据可用信息，答案是：分析完成。"
    
    def run(self, question):
        """执行ReAct循环"""
        print(f"🤖 ReAct Agent | 问题：{question}\n")
        
        step = 0
        while step < self.max_steps:
            step += 1
            print(f"  Step {step}:")
            
            # 1. 构建带历史的Prompt
            history_str = "\n".join(self.history[-6:]) if self.history else "暂无"
            prompt = REACT_PROMPT_TEMPLATE.format(
                history=history_str,
                question=question
            )
            
            # 2. 调用LLM
            raw_output = self._call_llm(prompt)
            parsed = self._parse_action(raw_output)
            
            print(f"    {parsed['type'].upper()}: {raw_output.split(':', 1)[-1].strip()[:100]}")
            
            # 3. 执行
            if parsed["type"] == "final":
                print(f"\n  ✅ 最终答案：{parsed['content']}")
                return parsed["content"]
            
            elif parsed["type"] == "action":
                tool_name = parsed["tool"]
                params = parsed["params"]
                
                # 执行工具
                tool_func = Tools.TOOL_MAP.get(tool_name)
                if tool_func:
                    result = tool_func(params)
                    print(f"    → 工具结果：{result[:80]}")
                    
                    # 记录到历史
                    self.history.append(f"Action: {tool_name} | {params}")
                    self.history.append(f"Observation: {result}")
                else:
                    print(f"    → 未知工具：{tool_name}")
            
            elif parsed["type"] == "thought":
                self.history.append(f"Thought: {parsed['content']}")
        
        return "已达最大步数，任务结束"

# ========== 多步ReAct循环示例 ==========
class MultiStepReAct:
    """多步ReAct示例"""
    
    @staticmethod
    def demonstrate():
        steps = [
            ("Thought", "用户想知道天气并做决策，需要先查天气"),
            ("Action", "get_weather | 北京"),
            ("Observation", "北京：晴，22℃"),
            ("Thought", "天气不错，适合户外活动，但还需要计算时间"),
            ("Action", "get_time"),
            ("Observation", "当前是周末下午"),
            ("Thought", "现在是周末且天气好，可以建议户外活动"),
            ("Final Answer", "北京今天天气晴朗，22℃，非常适合户外活动。建议去公园散步或爬山。")
        ]
        
        print("多步ReAct循环示例：")
        print(f"\n{'步骤':<8}{'类型':<16}{'内容'}")
        print("-" * 60)
        for i, (type_, content) in enumerate(steps, 1):
            print(f"Step{i:<4}{type_:<16}{content[:40]}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 ReAct模式深度剖析")
    print("推理(Reasoning) + 行动(Action) 循环")
    print("=" * 60)
    
    print("\n📋 ReAct完整流程演示")
    print("-" * 40)
    agent = ReActAgent()
    result = agent.run("北京今天天气怎么样？适合做什么？")
    
    print("\n\n📊 多步ReAct")
    print("-" * 40)
    MultiStepReAct.demonstrate()
    
    print("\n" + "=" * 60)
    print("💡 ReAct vs 传统模式对比")
    print("=" * 60)
    print("""
传统模式：用户输入 → LLM直接输出
  问题：今天适合出门吗？
  输出：建议您查看天气预报（模糊建议）

ReAct模式：用户输入 → 思考 → 行动 → 观察 → 再思考 → 最终输出
  问题：今天适合出门吗？
  Thought: 需要先查天气
  Action: get_weather | 北京
  Observation: 晴，22℃
  Final: 天气晴朗，温度舒适，适合出门
  （有依据、可验证、更精准）
""")
