# 第4篇配套代码：记忆模块详解 - AI Agent的三级记忆系统
# 展示瞬时记忆、短期记忆、长期记忆的工作原理
# 运行：python 01_memory_demo.py

import json
from datetime import datetime

# ========== 1. 模拟长期记忆库 ==========
long_term_memory = []

def save_memory(item, category="general", importance=1):
    """写入记忆"""
    memory_entry = {
        "content": item,
        "category": category,
        "importance": importance,
        "time": datetime.now().isoformat()
    }
    long_term_memory.append(memory_entry)
    return memory_entry

def retrieve_memory(query, top_k=3):
    """检索记忆（简化版，真实场景使用向量检索）"""
    # 基于关键词匹配的简单检索
    scored = []
    for item in long_term_memory:
        score = 0
        if query in item["content"]:
            score += item["importance"] * 2
        # 检查分类
        if any(word in query for word in item["category"].split()):
            score += 1
        if score > 0:
            scored.append((score, item))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in scored[:top_k]]

def generate_reply(user_input):
    """带记忆的回复生成"""
    memory = retrieve_memory(user_input)
    memory_context = "\n".join([m["content"] for m in memory]) if memory else "无相关记忆"
    
    prompt = f"""
用户输入：{user_input}
历史记忆：{memory_context}
请参考历史记忆，生成符合用户偏好的回复。
"""
    print(f"[思考] 检索到{len(memory)}条相关记忆")
    return f"[回复] 基于'{memory_context[:50]}...'生成：针对「{user_input}」的回复"

# ========== 2. 完整三级记忆系统 ==========
class MemorySystem:
    """三级记忆系统"""
    
    def __init__(self):
        # 瞬时记忆：当前对话上下文（窗口内）
        self.working_memory = []
        # 短期记忆：最近N条对话
        self.short_term = []
        # 长期记忆：持久化存储
        self.long_term = []
        
        # 记忆容量限制
        self.WORKING_LIMIT = 5
        self.SHORT_TERM_LIMIT = 50
    
    def add_message(self, role, content):
        """添加消息到工作记忆"""
        msg = {"role": role, "content": content, "time": datetime.now().isoformat()}
        self.working_memory.append(msg)
        
        # 工作记忆满了，压缩到短期记忆
        if len(self.working_memory) > self.WORKING_LIMIT:
            self._compress_to_short_term()
        
        return msg
    
    def _compress_to_short_term(self):
        """压缩工作记忆到短期记忆"""
        # 保留最近的几条
        recent = self.working_memory[-3:]
        self.short_term.extend(recent)
        
        # 短期记忆超过限制，压缩到长期记忆
        if len(self.short_term) > self.SHORT_TERM_LIMIT:
            self._summarize_to_long_term()
        
        # 清空工作记忆（保留最近的2条作为上下文）
        self.working_memory = self.working_memory[-2:]
    
    def _summarize_to_long_term(self):
        """将短期记忆总结后存入长期记忆"""
        # 提取重要信息
        important_points = []
        for msg in self.short_term[-20:]:
            if msg["role"] == "user":
                important_points.append(f"用户关注：{msg['content'][:50]}")
            elif msg["role"] == "assistant":
                if "偏好" in msg["content"] or "喜欢" in msg["content"]:
                    important_points.append(f"用户偏好：{msg['content'][:50]}")
        
        if important_points:
            self.long_term.append({
                "summary": important_points[-5:],  # 只保留最重要的5条
                "time": datetime.now().isoformat()
            })
        
        # 清空短期记忆（保留最近的10条）
        self.short_term = self.short_term[-10:]
    
    def get_context(self):
        """获取完整的记忆上下文"""
        context = {
            "working_memory": self.working_memory,
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "long_term_summary": self.long_term[-3:] if self.long_term else []
        }
        return context

# ========== 3. 向量记忆检索（模拟） ==========
class VectorMemory:
    """基于向量的记忆检索（模拟）"""
    
    def __init__(self):
        self.memories = {}
    
    def add_memory(self, key, content, tags=None):
        self.memories[key] = {
            "content": content,
            "tags": tags or [],
            "embedding_simulated": hash(key) % 1000
        }
    
    def semantic_search(self, query, top_k=3):
        """语义搜索（使用简单的关键词 + 标签匹配模拟）"""
        results = []
        query_lower = query.lower()
        for key, mem in self.memories.items():
            score = 0
            if query_lower in key.lower():
                score += 10
            if query_lower in mem["content"].lower():
                score += 5
            for tag in mem["tags"]:
                if tag in query_lower:
                    score += 3
            if score > 0:
                results.append({"key": key, "content": mem["content"], "score": score})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 AI Agent 记忆模块详解")
    print("三级记忆系统：工作记忆 → 短期记忆 → 长期记忆")
    print("=" * 60)
    
    # 1. 基础记忆操作
    print("\n1️⃣ 基础记忆操作")
    print("-" * 40)
    save_memory("用户周报喜欢结果先行，突出数据和进度。", "工作偏好", importance=5)
    save_memory("用户经常用Python做数据分析", "技能", importance=3)
    save_memory("用户负责产品团队，关注KPI完成率", "工作信息", importance=4)
    
    result = generate_reply("帮我写本周工作总结。")
    print(f"  {result}")
    
    # 2. 三级记忆系统
    print("\n2️⃣ 三级记忆系统演示")
    print("-" * 40)
    ms = MemorySystem()
    
    # 模拟多轮对话
    conversation = [
        ("user", "你好，我想了解一下你们的定价"),
        ("assistant", "您好！我们有基础版¥99/月，专业版¥299/月，企业版需定制"),
        ("user", "专业版包含哪些功能？"),
        ("assistant", "专业版包含所有基础功能+高级分析+API接口"),
        ("user", "好的，我比较关注API接口的调用次数限制"),
        ("assistant", "专业版API调用限制为10000次/月"),
        ("user", "那企业版呢？"),
        ("assistant", "企业版不限次数，支持私有化部署，需联系我们定制报价")
    ]
    
    for role, content in conversation:
        ms.add_message(role, content)
    
    context = ms.get_context()
    print(f"  工作记忆条数：{len(context['working_memory'])}")
    print(f"  短期记忆条数：{context['short_term_count']}")
    print(f"  长期记忆条数：{context['long_term_count']}")
    
    if context['long_term_summary']:
        print(f"  长期记忆摘要：{context['long_term_summary'][0]['summary'][:100]}")
    
    # 3. 向量记忆检索
    print("\n3️⃣ 语义检索演示")
    print("-" * 40)
    vm = VectorMemory()
    vm.add_memory("周报格式", "用户偏好：结果先行，数据驱动", ["工作", "偏好"])
    vm.add_memory("编程语言", "用户主要用Python做数据分析", ["技能", "Python"])
    vm.add_memory("会议记录", "用户上周参会讨论了Q2产品路线图", ["工作", "会议"])
    
    results = vm.semantic_search("用户偏好周报")
    for r in results:
        print(f"  [评分{r['score']}] {r['key']}：{r['content']}")
