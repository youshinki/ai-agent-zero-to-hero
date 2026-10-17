# 第15篇：智能记忆压缩实战 | 彻底解决Token爆炸，实现无限对话记忆

欢迎回到 **AI Agent 零基础实战** 连载系列。

上一篇第14篇，我们给AI Agent装上了**持久化长期记忆**：对话刷新不丢、服务重启不丢、全程上下文连续对话。但是！持久化记忆带来了一个致命工程级BUG——**Token爆炸**。

# 一、所有长期记忆Agent的通病：Token爆炸

![](images/15_1.jpg)

随着聊天轮次变多，历史对话越来越长，传给大模型的上下文越来越大，导致Token消耗指数级上涨、响应速度越来越慢、最终直接超出模型上下文窗口报错崩溃。这就是90%新手做不出真正长期AI助手的根本原因：**只会存记忆，不会精简记忆**。

普通ChatGPT、Claude、商业AI底层全部自带：记忆摘要、滚动压缩、智能遗忘、重点留存。没有压缩机制的记忆 = 一次性报废的记忆。本篇带你从零手写**工业级智能记忆压缩系统**，彻底根治Token爆炸。

# 二、核心原理：为什么必须做记忆压缩

![](images/15_2.jpg)

## 1. 原始记忆模式

每一轮完整历史+新问题全部投喂模型。缺点：对话10轮上下文翻倍，50轮Token爆炸，100轮直接溢出报错。

## 2. 智能压缩模式

系统自动判断：对话较短则完整保留；对话过长则智能摘要压缩，只存核心逻辑。最终效果：历史无限叠加，但上下文永远保持轻量化。

## 3. 压缩核心逻辑

- 近期对话：完整细节保留（保证连贯）
- 远期对话：摘要核心留存（减少体积）
- 冗余话术：自动过滤清洗
- 关键设定：永久锁定不丢失

# 三、升级后全新项目结构

![](images/15_3.jpg)

仅新增记忆压缩模块，完全兼容前14篇所有代码。

```text
agent_api_service/
├── index.html        # 前端界面（无改动）
├── main.py           # 服务入口（新增压缩接口）
├── agent_core.py     # Agent核心（新增记忆压缩函数）
├── config.py
├── .env
├── chat_memory/
│   └── history.json
└── memory_utils.py   # 【全新新增】记忆压缩工具库
```

# 四、全新工具模块：memory_utils.py（核心代码）

```python
from openai import OpenAI
from config import MODEL_API_KEY, MODEL_BASE_URL, MODEL_NAME
client = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)

COMPRESS_THRESHOLD = 20  # 超过20轮自动触发压缩
KEEP_RECENT = 10         # 保留最近10轮完整对话

def count_message_tokens(msg_list):
    total = 0
    for item in msg_list:
        total += len(item.get("content", ""))
    return total

def compress_history(history_list):
    """智能压缩：保留近期完整，将更早对话压缩为摘要"""
    if len(history_list) < COMPRESS_THRESHOLD:
        return history_list
    old_history = history_list[:-KEEP_RECENT]
    recent_history = history_list[-KEEP_RECENT:]
    concat_text = ""
    for item in old_history:
        role = "用户" if item["role"] == "user" else "AI"
        concat_text += f"{role}：{item['content']}\n"
    prompt = f"""
请对以下历史对话进行极致精简摘要：
1. 保留用户核心身份、需求、设定、关键结论
2. 删除客套话、重复话、冗余对话
3. 输出结构化总结，方便后续AI接续对话
4. 尽量短、信息密度最高
历史对话：
{concat_text}
    """
    res = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role":"user", "content":prompt}]
    )
    summary = res.choices[0].message.content
    compressed_item = {"role":"system",
        "content": f"【历史对话摘要】{summary}"}
    new_history = [compressed_item] + recent_history
    return new_history
```

# 五、升级 agent_core.py（适配压缩记忆）

```python
from openai import OpenAI
from config import MODEL_API_KEY, MODEL_BASE_URL, MODEL_NAME
from memory_utils import compress_history

client = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)

class BaseAgent:
    def __init__(self):
        self.history = []

    def load_history(self, history_list):
        self.history = compress_history(history_list)

    def plan_task(self, user_input):
        context = ""
        if self.history:
            context = f"历史对话记录：{self.history}\n"
        prompt = f"""
你是专业AI任务规划师，请结合历史对话分步思考当前任务。
{context}
当前用户新需求：{user_input}
请严格输出：1.任务核心目标 2.任务拆解步骤 3.本次执行注意事项
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}])
        return res.choices[0].message.content

    def execute_task(self, user_input, plan_result):
        context = ""
        if self.history:
            context = f"历史对话记录：{self.history}\n"
        prompt = f"""
结合历史对话与任务规划，完整落地执行：
{context}
当前需求：{user_input}
任务规划：{plan_result}
输出完整、连贯、贴合上下文的最终内容。
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}])
        return res.choices[0].message.content

    def reflect_task(self, user_input, raw_result):
        context = ""
        if self.history:
            context = f"历史对话记录：{self.history}\n"
        prompt = f"""
结合历史对话自查本次回答是否连贯合理：
{context}
当前需求：{user_input}
原始输出：{raw_result}
自查：连贯性、完整性、是否遗忘上文、是否逻辑冲突
输出：问题清单 + 最终优化答案
        """
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}])
        return res.choices[0].message.content

    def run_with_history(self, user_task, history_list):
        self.load_history(history_list)
        plan = self.plan_task(user_task)
        raw = self.execute_task(user_task, plan)
        final = self.reflect_task(user_task, raw)
        return {"user_task":user_task,"plan":plan,
                "raw_result":raw,"final_result":final}

agent = BaseAgent()
```

# 六、升级 main.py（自动压缩持久化）

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from agent_core import agent
from memory_utils import compress_history
import json, os

app = FastAPI(title="无限记忆AI Agent服务", version="3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

MEMORY_DIR = "chat_memory"
MEMORY_FILE = os.path.join(MEMORY_DIR, "history.json")
os.makedirs(MEMORY_DIR, exist_ok=True)
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

class ChatRequest(BaseModel):
    task: str
    history: list

@app.post("/api/agent/stream")
async def stream_chat(req: ChatRequest):
    try:
        compressed_hist = compress_history(req.history)
        result = agent.run_with_history(req.task, compressed_hist)
        final_text = result["final_result"]
        req.history.append({"role":"user","content":req.task})
        req.history.append({"role":"assistant","content":final_text})
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(req.history, f, ensure_ascii=False, indent=2)
        def stream():
            for char in final_text:
                yield json.dumps({"char":char}, ensure_ascii=False)+"\n"
        return StreamingResponse(stream(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/history")
async def get_history():
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return {"code":200, "history": json.load(f)}

@app.post("/api/agent/clear")
async def clear_history():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
    return {"code":200, "msg":"记忆已清空"}

@app.get("/health")
async def health():
    return {"code":200, "msg":"无限记忆Agent服务正常"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

# 七、前端无需改动

index.html 完全不用改。所有压缩、优化、防爆炸逻辑全部在后端静默完成，用户无感知、体验丝滑升级。

# 八、实测效果

![](images/15_4.jpg)

**旧版本：**聊30轮卡顿明显，聊50轮Token超标报错。 **新版本：**聊100轮丝滑流畅，聊500轮上下文依旧轻巧，永久不爆炸、不溢出、可接续。

记忆特点：近期对话细节完整、回答精准；远期对话核心留存、无冗余；用户人设、偏好、任务目标永久记住。重点：磁盘保存完整原始对话记录，送入模型推理的才是压缩版本。

# 九、工业级优化参数可调

```python
COMPRESS_THRESHOLD = 20   # 触发压缩轮次
KEEP_RECENT = 10          # 保留最新完整轮次
```

轻量化场景调小参数，高精度对话调大参数。

# 十、本篇核心总结

- 只存不压 = 必死的AI记忆
- Token爆炸是所有长期AI助手的最大拦路虎
- 冷热分离记忆架构：远期摘要 + 近期完整
- 全自动无感知压缩，用户零负担
- 真正实现永久无限对话智能体

至此，你的Agent彻底脱离玩具级，进入私人专属AI助理级别。下期预告：第16篇｜智能Agent定时任务&自动后台执行，让AI脱离手动触发！

# 📝 面试高频问答

**Q1：什么是Token爆炸？长期记忆Agent为什么会出现这个问题？**答：对话轮次不断上涨，上下文Token持续膨胀，超出模型窗口上限报错；只做记忆持久化、没有记忆压缩就会出现。

**Q2：冷热分离记忆压缩的思路是什么？**答：近期N轮对话完整保留保障回答细节；更早的远期对话用LLM做摘要只保留关键信息，减少送入模型的上下文体积。

**Q3：原始历史记录和压缩后的上下文怎么处理？**答：磁盘持久化存储完整原始对话；送入模型推理使用压缩版本，保证原始数据不丢失。

**Q4：如果业务对对话精度要求很高，怎么调整压缩参数？**答：调大 COMPRESS_THRESHOLD 触发阈值，调大 KEEP_RECENT 保留完整轮次，牺牲部分Token换取更高对话精度。

**Q5：记忆压缩除了LLM摘要，还有哪些常见方案？**答：滑动窗口直接丢弃最早消息；向量记忆抽取关键片段；MemGPT分层记忆。

> 来源：头条号《AI Agent 零基础实战》第15篇｜版权归作者所有，仅供学习交流
