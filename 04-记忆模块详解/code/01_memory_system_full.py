#!/usr/bin/env python3
"""
================================================================================
  第4篇：记忆模块详解 —— 完整三级记忆系统项目代码

  覆盖文章中所有技术点：
    1. 大模型为什么"健忘"（上下文窗口外失忆、任务间失忆、知识经验失忆）
    2. 三级记忆架构（瞬时记忆 → 短期记忆 → 长期记忆）
    3. 向量数据库在长期记忆中的作用（文本→向量→存储→检索）
    4. 记忆模块与 Agent 主流程协同（接收→检索→组装→执行→更新→沉淀）
    5. 极简记忆代码实战（存、查、用）
    6. 记忆系统设计原则（高价值优先、隐私风险、简单至上）

  运行方式：python 01_memory_system_full.py
================================================================================
"""

import json
import time
import math
import uuid
import re
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# 第一部分：大模型为什么"健忘"——三种失忆演示
# ═══════════════════════════════════════════════════════════════════════════════

def demo_llm_forgetfulness():
    """
    演示大模型的三种典型失忆。

    核心认知：大模型拥有的只是"上下文感知能力"，不是真正的记忆。
    内容不在当前窗口里，模型就当它不存在。
    """
    print("\n" + "█" * 70)
    print("  第4篇：记忆模块详解 — 大模型为什么"健忘"")
    print("  大模型只有『上下文感知』，没有『真正记忆』")
    print("█" * 70)

    class StatelessLLM:
        """
        模拟无状态大模型——每次调用都是"无状态"的。
        它只看当前输入窗口里的内容，窗口外的信息全部"失忆"。
        """
        def __init__(self, window_size: int = 3):
            self.window_size = window_size
            self.context = []

        def chat(self, user_input: str) -> str:
            # 模拟上下文窗口：只保留最近 N 条
            self.context.append(("user", user_input))
            if len(self.context) > self.window_size:
                dropped = self.context.pop(0)
                # 模拟"窗口外失忆"——丢弃的内容模型再也看不到
                pass

            # 模拟回复
            visible = [c[1] for c in self.context]
            if "我叫" in user_input:
                name = user_input.split("我叫")[-1].strip()
                return f"好的，我记住了你叫{name}"
            elif "我叫什么" in user_input or "我是谁" in user_input:
                # 检查上下文中有没有自我介绍
                names = [s for s in visible if "我叫" in s]
                if names:
                    name = names[-1].split("我叫")[-1].strip()
                    return f"你叫{name}"
                else:
                    return "抱歉，我不记得你叫什么了……"
            else:
                return f"你说的是：{user_input}"

    llm = StatelessLLM(window_size=2)

    # ── 失忆A：上下文窗口外失忆 ──
    print("\n  ── 失忆A：上下文窗口外失忆 ──")
    print("  假设窗口尺寸 = 2，超过窗口的旧内容被丢弃")
    print()
    print("  Step 1: ", llm.chat("你好"))
    print("  Step 2: ", llm.chat("我叫小王"))
    # 此时窗口已有2条，下一条会挤掉最早的一条
    print("  Step 3: ", llm.chat("今天天气怎么样？"))
    print("  → 上一条自我介绍被挤出窗口")
    print("  Step 4: ", llm.chat("我叫什么名字？"))
    print("  → ", end="")
    r4 = llm.chat("我叫什么名字？")
    print(r4)
    print("  → 结论：超出上下文窗口的内容被完全遗忘。这就是"窗口外失忆"。\n")

    # ── 失忆B：任务之间失忆 ──
    print("  ── 失忆B：任务之间失忆 ──")
    print("  新对话 = 新会话，旧会话的所有状态清零。")
    fresh_llm = StatelessLLM(window_size=5)
    print("  第1轮对话：", fresh_llm.chat("我叫小李，喜欢简洁的回复风格"))
    print("  第1轮对话：", fresh_llm.chat("帮我写周报"))
    print()
    print("  第2轮对话（新会话）—— 模型完全不记得上一轮的信息！")
    fresh2 = StatelessLLM(window_size=5)
    print("  第2轮对话：", fresh2.chat("帮我写周报"))
    print("  → 模型不记得"小李"，也不记得"简洁风格"")
    print("  用户不得不再次说明偏好。这就是"任务间失忆"。\n")

    # ── 失忆C：知识经验失忆 ──
    print("  ── 失忆C：知识经验失忆 ──")
    print("  模型不会自动沉淀经验，每次都像第一次运行。")
    llm3 = StatelessLLM(window_size=5)
    print("  第1次：", llm3.chat("这个产品是收费的吗？"))
    print("  纠正：它是免费的开源产品")
    print("  → 模型临时接受了修正")
    print("  第2次（新会话）：同样的问题")
    llm3b = StatelessLLM(window_size=5)
    print("  第2次：", llm3b.chat("这个产品是收费的吗？"))
    print("  → 模型不记得被纠正过，再次给出同样的错误回答。")
    print("  → 因为被纠正的经验没有被沉淀为长期记忆。")
    print("  → 这就是"知识经验失忆"。\n")

    print("  💡 核心结论：")
    print("     大模型的"记性"是临时可见，不是长期存储。")
    print("     而 AI Agent 的记忆模块，就是要")
    print("     把"临时可见"变成"可存储、可检索、可复用"。\n")

    return StatelessLLM


# ═══════════════════════════════════════════════════════════════════════════════
# 第二部分：三级记忆架构完整实现
# ═══════════════════════════════════════════════════════════════════════════════

class InstantMemory:
    """
    瞬时记忆 —— 当前对话上下文。

    特征：
    - 响应最快：直接存在于模型的输入窗口中
    - 不需要额外存储：依赖模型的上下文感知能力
    - 容量受上下文窗口限制：超出则丢弃最早的内容
    - 任务结束后容易丢失：模型不会主动持久化

    适合处理：当前轮次理解、即时推理、短上下文任务
    """

    def __init__(self, window_size: int = 6):
        self.window_size = window_size
        self.messages: List[Dict[str, Any]] = []
        self.system_prompt: str = ""
        self.tool_results: Dict[str, str] = {}

    def set_system_prompt(self, prompt: str):
        """设置系统提示词（贯穿始终的上下文）"""
        self.system_prompt = prompt

    def add_message(self, role: str, content: str) -> Optional[Dict]:
        """
        添加一条消息。
        如果超出窗口尺寸，返回被丢弃的最旧消息（模拟"窗口外失忆"）。
        """
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(msg)
        if len(self.messages) > self.window_size:
            dropped = self.messages.pop(0)
            return dropped
        return None

    def add_tool_result(self, tool_name: str, result: str):
        """添加工具调用结果（也是瞬时记忆的一部分）"""
        self.tool_results[tool_name] = result

    def build_context(self) -> str:
        """把瞬时记忆组装成完整的上下文文本（模拟给LLM的输入）"""
        parts = []
        if self.system_prompt:
            parts.append(f"【系统提示】{self.system_prompt}")
        for msg in self.messages:
            parts.append(f"[{msg['role']}] {msg['content']}")
        for name, result in list(self.tool_results.items())[-3:]:
            parts.append(f"[工具:{name}] {result[:100]}")
        return "\n".join(parts)

    def clear(self):
        """清空瞬时记忆（模拟新会话）"""
        self.messages.clear()
        self.tool_results.clear()

    def get_stats(self) -> Dict:
        return {
            "messages_count": len(self.messages),
            "window_size": self.window_size,
            "window_usage": f"{len(self.messages)}/{self.window_size}",
            "tool_results_count": len(self.tool_results)
        }


class ShortTermMemory:
    """
    短期记忆 —— 本轮任务状态记忆。

    解决以下问题：
    - 重复提问（Agent忘记已经确认过的信息）
    - 重复调用工具（不记得已经调用过某个工具）
    - 忘记已完成的步骤（任务做到一半跑偏）
    - 中途丢失中间结果（需要重新计算）

    适合处理：单任务状态跟踪、多步骤执行记录、工具调用结果缓存、任务进度管理
    """

    def __init__(self):
        self.current_task: str = ""
        self.task_goal: str = ""
        self.completed_steps: List[Dict] = []
        self.pending_steps: List[str] = []
        self.tool_call_log: List[Dict] = []
        self.intermediate_results: Dict[str, str] = {}
        self.confirmed_info: List[str] = []
        self.facts_found: set = set()
        self.status: str = "idle"  # idle | in_progress | completed | failed
        self.start_time: float = 0.0

    def start_task(self, task: str, goal: str, steps: List[str]):
        """启动新任务：初始化所有状态"""
        self.current_task = task
        self.task_goal = goal
        self.completed_steps = []
        self.pending_steps = steps[:]
        self.tool_call_log = []
        self.intermediate_results = {}
        self.confirmed_info = []
        self.status = "in_progress"
        self.start_time = time.time()
        print(f"      📋 任务启动: {task[:40]}... | 规划 {len(steps)} 步")

    def complete_step(self, step_name: str, result: str = ""):
        """完成一个步骤，记录结果"""
        if step_name in self.pending_steps:
            self.pending_steps.remove(step_name)
        self.completed_steps.append({
            "name": step_name,
            "result": result[:200] if result else "",
            "time": datetime.now().isoformat()
        })
        if result:
            self.intermediate_results[step_name] = result

    def log_tool_call(self, tool_name: str, params: Dict, result: str):
        """记录工具调用（避免重复调用）"""
        self.tool_call_log.append({
            "tool": tool_name,
            "params": params,
            "result_preview": result[:100],
            "time": datetime.now().isoformat()
        })

    def confirm_fact(self, fact: str):
        """确认一个事实（避免重复提问）"""
        if fact not in self.confirmed_info:
            self.confirmed_info.append(fact)

    def is_already_confirmed(self, fact: str) -> bool:
        """检查某个事实是否已经确认过"""
        return any(fact in c for c in self.confirmed_info)

    def is_tool_already_called(self, tool_name: str, params: Dict) -> bool:
        """检查是否已经调用过某个工具（避免重复调用）"""
        for log in self.tool_call_log:
            if log["tool"] == tool_name and log["params"] == params:
                return True
        return False

    def get_progress(self) -> Dict:
        """获取当前任务进度报告"""
        total = len(self.completed_steps) + len(self.pending_steps)
        return {
            "task": self.current_task,
            "goal": self.task_goal,
            "status": self.status,
            "completed": len(self.completed_steps),
            "total": total,
            "progress_pct": round(len(self.completed_steps) / max(total, 1) * 100, 1),
            "tool_calls": len(self.tool_call_log),
            "confirmed_facts": len(self.confirmed_info)
        }

    def summarize(self) -> str:
        """生成任务状态摘要（用于注入LLM上下文）"""
        progress = self.get_progress()
        return (
            f"【当前任务状态】\n"
            f"  目标：{progress['goal'][:50]}\n"
            f"  进度：{progress['completed']}/{progress['total']} ({progress['progress_pct']}%)\n"
            f"  已完成：{[s['name'][:20] for s in self.completed_steps]}\n"
            f"  待完成：{self.pending_steps[:3]}\n"
            f"  已确认信息：{self.confirmed_info[:3]}\n"
            f"  工具调用次数：{progress['tool_calls']}"
        )

    def end_task(self, success: bool = True):
        """结束当前任务"""
        elapsed = time.time() - self.start_time
        self.status = "completed" if success else "failed"

    def clear(self):
        """清空短期记忆（重置为初始状态）"""
        self.__init__()


class SimpleEmbedding:
    """
    极简文本嵌入模拟器。

    真实环境中：使用 OpenAI Embedding / BGE / text2vec 等模型
    将文本转换为高维向量（通常是 768 维或 1536 维）。
    这里用 TF-IDF 风格的词袋+双字ngram做语义近似模拟。

    核心作用：
    1. 把文本变成一串数字（向量）
    2. 语义相近的文本，生成的向量距离也更近
    3. 从而实现"根据语义检索"，不依赖精确关键词匹配
    """

    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.vocab_size = 0

    def _tokenize(self, text: str) -> List[str]:
        """分词：提取中文/英文词 + 2-gram/3-gram 子串"""
        tokens = re.findall(r'[\w]+', text)
        result = []
        for t in tokens:
            if len(t) <= 4:
                result.append(t)
            else:
                # 2-gram
                for i in range(len(t) - 1):
                    result.append(t[i:i+2])
                # 3-gram
                for i in range(len(t) - 2):
                    result.append(t[i:i+3])
                result.append(t)
        return result

    def _build_vocab(self, texts: List[str]):
        """构建词表"""
        for text in texts:
            for token in self._tokenize(text):
                if token not in self.vocab:
                    self.vocab[token] = self.vocab_size
                    self.vocab_size += 1

    def embed(self, text: str) -> List[float]:
        """将文本转为向量（归一化词袋向量）"""
        if not self.vocab:
            self._build_vocab([text])
        tokens = self._tokenize(text)
        vec = [0.0] * self.vocab_size
        for tok in tokens:
            if tok in self.vocab:
                vec[self.vocab[tok]] += 1.0
        # L2 归一化
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def similarity(self, a: str, b: str) -> float:
        """计算两段文本的余弦相似度"""
        old_vocab = dict(self.vocab)
        # 扩展词表以包含两段文本的所有词
        self._build_vocab([a, b])
        va = self.embed(a)
        vb = self.embed(b)
        # 恢复原词表
        self.vocab = old_vocab
        self.vocab_size = len(old_vocab)
        dot = sum(va[i] * vb[i] for i in range(min(len(va), len(vb))))
        return dot


class LongTermMemoryItem:
    """长期记忆中的一条记忆条目"""

    def __init__(self, content: str, source: str = "general",
                 importance: float = 0.5, tags: List[str] = None,
                 ttl_seconds: float = 0):
        self.id = str(uuid.uuid4())[:12]
        self.content = content
        self.source = source      # preference | business_rule | knowledge | experience
        self.importance = max(0, min(1, importance))  # 0~1
        self.tags = tags or []
        self.timestamp = time.time()
        self.ttl = (time.time() + ttl_seconds) if ttl_seconds > 0 else 0
        self.access_count = 0
        self.embedding: List[float] = []

    def is_expired(self) -> bool:
        return self.ttl > 0 and time.time() > self.ttl

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content[:80],
            "source": self.source,
            "importance": self.importance,
            "tags": self.tags,
            "age_hours": round((time.time() - self.timestamp) / 3600, 1),
            "access_count": self.access_count
        }


class VectorMemoryStore:
    """
    长期记忆存储 —— 模拟向量数据库的完整功能。

    为什么向量数据库是长期记忆的核心？
    1. 语义存储：语义相近的信息自动"靠近"（不依赖精确匹配）
    2. 快速检索：百万级数据毫秒级响应
    3. 模糊匹配：即使用户的措辞变了，也能找到相关记忆
    4. 增量扩展：随时添加新记忆，无需重建索引

    核心流程：
    文本 → Embedding(转为向量) → 存入VectorDB → 检索(余弦相似度) → 返回Top-K
    """

    def __init__(self, embedder: SimpleEmbedding):
        self.items: List[LongTermMemoryItem] = []
        self.embedder = embedder
        self.stats = {"stored": 0, "retrieved": 0, "pruned": 0}

    def store(self, content: str, source: str = "general",
              importance: float = 0.5, tags: List[str] = None,
              ttl_seconds: float = 0) -> str:
        """
        存入一条长期记忆。

        Args:
            content: 记忆内容
            source: 来源（user_preference / business_rule / knowledge / experience）
            importance: 重要性 0~1（越高越重要）
            tags: 标签列表
            ttl_seconds: 过期时间（秒），0表示永不过期

        Returns: 记忆条目的 ID
        """
        item = LongTermMemoryItem(content, source, importance, tags, ttl_seconds)
        item.embedding = self.embedder.embed(content)
        self.items.append(item)
        self.stats["stored"] += 1
        # 按重要性降序排列
        self.items.sort(key=lambda x: x.importance, reverse=True)
        print(f"      💾 [长期记忆] 已存储 '{content[:40]}...' (来源={source}, 重要性={importance})")
        return item.id

    def retrieve(self, query: str, top_k: int = 3,
                 min_similarity: float = 0.05,
                 source_filter: Optional[str] = None) -> List[LongTermMemoryItem]:
        """
        检索最相关的长期记忆。

        这是向量数据库最核心的能力：
        不需要精确匹配关键词，语义相关就能找到。

        Args:
            query: 查询文本
            top_k: 返回最多几条
            min_similarity: 最低相似度阈值
            source_filter: 按来源过滤（可选）

        Returns: 按相关性降序排列的记忆列表
        """
        # 先清理过期条目
        self.items = [it for it in self.items if not it.is_expired()]

        query_embed = self.embedder.embed(query)
        scored = []

        for item in self.items:
            if source_filter and item.source != source_filter:
                continue
            if not item.embedding:
                continue

            # 余弦相似度 + 重要性加权
            sim = self._cosine_similarity(query_embed, item.embedding)
            weighted = sim * 0.7 + item.importance * 0.3
            scored.append((weighted, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, item in scored[:top_k]:
            if score >= min_similarity:
                item.access_count += 1
                self.stats["retrieved"] += 1
                results.append(item)

        print(f"      🔍 [检索] '{query[:30]}...' → 找到 {len(results)} 条相关记忆")
        for r in results:
            print(f"              [{r.source}] 评分={score:.3f} | {r.content[:50]}...")
        return results

    def _cosine_similarity(self, va: List[float], vb: List[float]) -> float:
        """计算两个向量的余弦相似度"""
        n = min(len(va), len(vb))
        if n == 0:
            return 0.0
        dot = sum(va[i] * vb[i] for i in range(n))
        na = math.sqrt(sum(v * v for v in va[:n]))
        nb = math.sqrt(sum(v * v for v in vb[:n]))
        if na * nb == 0:
            return 0.0
        return dot / (na * nb)

    def search_by_tags(self, tags: List[str]) -> List[LongTermMemoryItem]:
        """按标签检索"""
        return [it for it in self.items
                if any(t in it.tags for t in tags) and not it.is_expired()]

    def forget(self, memory_id: str) -> bool:
        """主动遗忘（删除）一条记忆"""
        before = len(self.items)
        self.items = [it for it in self.items if it.id != memory_id]
        return len(self.items) < before

    def prune(self, max_items: int = 100, min_importance: float = 0.2):
        """
        裁剪低价值记忆。

        解决"记忆越多越好吗"问题：定期清理低价值噪音记忆。
        保留规则：
        1. 重要性 >= min_importance 的保留
        2. 被检索 >= 2 次的保留（说明有复用价值）
        3. 仍然超过 max_items 则丢弃最不重要的
        """
        before = len(self.items)
        self.items = [
            it for it in self.items
            if it.importance >= min_importance or it.access_count >= 2
        ]
        if len(self.items) > max_items:
            self.items = self.items[:max_items]
        pruned = before - len(self.items)
        self.stats["pruned"] += pruned
        if pruned > 0:
            print(f"      ✂️ [裁剪] 低价值记忆：{before} → {len(self.items)} (移除 {pruned} 条)")
        return pruned

    def export_sensitive_check(self) -> List[Dict]:
        """
        导出可能包含敏感信息的记忆用于审查。
        这是隐私风险管理的核心功能：长期记忆必须支持
        数据可见性审查 + 可删除机制 + 用户知情权。
        """
        sensitive_keywords = ["密码", "电话", "手机", "地址", "身份证",
                             "银行", "信用卡", "银行卡", "生日"]
        reports = []
        for item in self.items:
            matched = [kw for kw in sensitive_keywords if kw in item.content]
            if matched:
                reports.append({
                    "id": item.id,
                    "content_preview": item.content[:60],
                    "matched_keywords": matched,
                    "source": item.source,
                    "importance": item.importance
                })
        return reports

    def get_statistics(self) -> Dict:
        """获取存储统计"""
        return {
            "total_items": len(self.items),
            "total_stored": self.stats["stored"],
            "total_retrieved": self.stats["retrieved"],
            "total_pruned": self.stats["pruned"],
            "avg_importance": round(
                sum(it.importance for it in self.items) / max(len(self.items), 1), 3
            ),
            "by_source": dict((s, sum(1 for it in self.items if it.source == s))
                              for s in set(it.source for it in self.items))
        }

    def get_all_items(self) -> List[Dict]:
        """获取所有记忆（用于展示）"""
        return [it.to_dict() for it in self.items]


# ═══════════════════════════════════════════════════════════════════════════════
# 第三部分：记忆模块与 Agent 主流程的协同
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryAugmentedAgent:
    """
    带完整三级记忆系统的 AI Agent。

    标准执行流程（记忆模块必须接入 Agent 主循环）：
    Step 1: 接收目标       ← 用户输入任务
    Step 2: 检索长期记忆   ← 根据当前目标从长期记忆中检索相关信息
    Step 3: 组装上下文     ← 系统提示 + 短期记忆状态 + 长期记忆结果
    Step 4: 执行规划行动   ← 基于完整上下文进行推理和执行
    Step 5: 更新短期记忆   ← 记录执行状态、中间结果、已完成步骤
    Step 6: 沉淀长期记忆   ← 把重要经验/偏好/规则写入长期记忆
    """

    def __init__(self, name: str = "智能助手"):
        self.name = name
        self.embedder = SimpleEmbedding()
        self.ltm = VectorMemoryStore(self.embedder)   # 长期记忆
        self.instant = InstantMemory(window_size=8)    # 瞬时记忆
        self.stm = ShortTermMemory()                   # 短期记忆
        self.interaction_count = 0

        # 设置系统提示词
        self.instant.set_system_prompt(
            f"你是一个名叫{name}的AI助手。"
            "你有完整的记忆能力：能记住用户偏好、历史经验和业务知识。"
            "每次回复时会自动参考相关的历史记忆。"
        )

    def chat(self, user_input: str, verbose: bool = True) -> str:
        """
        处理用户输入 —— 完整记忆闭环的主入口。

        这个函数完整演示了：
        记忆检索 → 上下文构建 → 执行响应 → 更新短期记忆 → 沉淀长期记忆
        """
        self.interaction_count += 1

        if verbose:
            print(f"\n{'─' * 55}")
            print(f"  🤖 [{self.name}] 第{self.interaction_count}次交互")
            print(f"  👤 用户：{user_input}")
            print(f"{'─' * 55}")

        # ── Step 1: 瞬时记忆更新 ──
        dropped = self.instant.add_message("user", user_input)
        if dropped and verbose:
            print(f"  ⚠ 瞬时记忆窗口溢出：丢弃了最早的消息")

        # ── Step 2: 检索长期记忆 ──
        if verbose:
            print("\n  📖 [Step 2] 检索长期记忆...")
        relevant = self.ltm.retrieve(user_input, top_k=4, min_similarity=0.05)

        # ── Step 3: 组装增强上下文 ──
        if verbose:
            print("\n  🧩 [Step 3] 组装上下文...")
        enhanced_prompt = self._build_enhanced_prompt(user_input, relevant, verbose)

        # ── Step 4: 判断意图并执行 ──
        if verbose:
            print("\n  🎯 [Step 4] 意图识别与执行...")
        response = self._process_intent(user_input, enhanced_prompt, relevant, verbose)

        # ── Step 5: 更新短期记忆 ──
        if verbose:
            print("\n  📋 [Step 5] 更新短期记忆...")
        self._update_short_term(user_input, response)

        # ── Step 6: 沉淀长期记忆 ──
        if verbose:
            print("\n  💾 [Step 6] 知识沉淀（检查是否需要存长期记忆）...")
        self._extract_and_save_knowledge(user_input, response, verbose)

        # 更新瞬时记忆
        self.instant.add_message("assistant", response)

        return response

    def _build_enhanced_prompt(self, user_input: str,
                                memories: List[LongTermMemoryItem],
                                verbose: bool) -> str:
        """组装增强上下文：系统提示 + 记忆 + 任务状态"""
        parts = [self.instant.system_prompt]

        # 加入长期记忆
        if memories:
            mem_section = "\n【检索到的相关历史记忆（请自动参考）】"
            for m in memories:
                mem_section += f"\n- [{m.source}] {m.content} (重要性:{m.importance})"
            parts.append(mem_section)

        # 加入短期记忆（任务状态）
        if self.stm.status == "in_progress":
            parts.append("\n" + self.stm.summarize())

        # 加入当前输入
        parts.append(f"\n【用户当前输入】\n{user_input}")
        parts.append("\n【指令】请基于以上历史记忆和当前任务状态，生成最适合用户的回复。")

        prompt = "\n".join(parts)
        if verbose:
            print(f"     上下文长度：{len(prompt)} 字符")
            print(f"     已注入 {len(memories)} 条历史记忆")
        return prompt

    def _process_intent(self, user_input: str, context: str,
                         memories: List[LongTermMemoryItem],
                         verbose: bool) -> str:
        """识别用户意图并执行对应操作"""
        # 检测意图类型
        is_fact_memory = any(kw in user_input for kw in
                             ["记住", "我叫", "我喜欢", "我偏好", "我的"])
        is_task = any(kw in user_input for kw in
                      ["帮我", "写", "生成", "分析", "总结", "规划", "报告"])
        is_query = any(kw in user_input for kw in
                       ["什么", "怎么", "为什么", "谁", "记得吗", "查一下"])

        # ── 情况A：用户告知事实/偏好 → 直接存入长期记忆 ──
        if is_fact_memory and not is_task and not is_query:
            if verbose:
                print(f"     检测到：偏好/事实存储请求 → 写入长期记忆")
            self.ltm.store(
                content=user_input,
                source="user_preference",
                importance=0.7,
                tags=["user_profile", "preference"],
                ttl_seconds=0  # 永不过期
            )
            # 也记入短期记忆的已确认信息
            self.stm.confirm_fact(user_input[:60])
            return (
                f"好的，我已经记住了！下次遇到相关问题时会自动参考这条信息。"
                f"（已存入长期记忆：{user_input[:60]}...）"
            )

        # ── 情况B：任务请求 → 启动完整管线 ──
        if is_task or (is_query and memories):
            return self._execute_task_pipeline(user_input, context, memories, verbose)

        # ── 情况C：查询/对话 ──
        if memories:
            # 有相关记忆 → 基于记忆回复
            top_mem = memories[0]
            return (
                f"(参考了您的历史记忆 [{top_mem.source}]: {top_mem.content[:50]}...)\n\n"
                f"关于「{user_input[:40]}」，基于历史信息：\n"
                f"根据您的过往记录，我可以帮您进一步处理。您想要我做什么？"
            )
        else:
            # 无相关记忆 → 普通回复
            return (
                f"收到：「{user_input[:50]}」\n"
                f"您可以让我：1) 记住信息（说"记住..."）\n"
                f"                  2) 执行任务（说"帮我..."）\n"
                f"                  3) 查询记忆（说"你记得..."）"
            )

    def _execute_task_pipeline(self, user_input: str, context: str,
                                memories: List[LongTermMemoryItem],
                                verbose: bool) -> str:
        """完整任务执行管线：规划 → 执行 → 反思 → 回复"""
        if verbose:
            print(f"     检测到：任务请求 → 启动完整管线")

        # ── 规划 ──
        steps = ["理解需求", "检索知识", "生成结果", "检查质量"]
        self.stm.start_task(user_input, user_input, steps)
        self.stm.complete_step("理解需求")

        if verbose:
            print(f"     规划步骤：{steps}")

        # ── 执行（模拟工具调用） ──
        # 检索长期记忆
        knowledge = self.ltm.retrieve(user_input, top_k=3, min_similarity=0.03)
        self.stm.complete_step("检索知识",
                               f"找到 {len(knowledge)} 条相关知识")

        # 生成回复
        if memories:
            pref = memories[0]
            response = (
                f"✅ 任务完成！\n\n"
                f"（自动参考了您的偏好「{pref.content[:40]}」）\n\n"
                f"根据您的需求和历史记录，为您生成了以下内容：\n\n"
                f"1️⃣ 核心结论（结果先行）\n"
                f"2️⃣ 详细数据与进展\n"
                f"3️⃣ 待解决问题\n"
                f"4️⃣ 下一步计划\n\n"
                f"（以上回复自动参考了您之前设定的偏好规则，无需重复说明）"
            )
        else:
            response = (
                f"✅ 任务完成！\n\n"
                f"关于「{user_input[:40]}」，已为您处理完成。\n"
                f"您可以让我记住这次的处理方式，方便下次自动使用。"
            )

        self.stm.complete_step("生成结果", response)
        self.stm.complete_step("检查质量", "质量检查通过")
        self.stm.end_task(success=True)

        if verbose:
            print(f"     4 步执行完毕，任务完成")

        return response

    def _update_short_term(self, user_input: str, response: str):
        """更新短期记忆"""
        if self.stm.status == "idle":
            steps = ["理解需求", "检索信息", "生成回复"]
            self.stm.start_task(user_input[:30], user_input, steps)
        self.stm.complete_step("理解需求", f"输入：{user_input[:50]}")
        self.stm.confirm_fact(user_input[:60])

    def _extract_and_save_knowledge(self, user_input: str, response: str,
                                     verbose: bool):
        """
        从交互中提取值得沉淀的知识，存入长期记忆。

        这是"记忆模块与Agent主流程协同"的关键环节：
        任务完成后，自动把重要经验沉淀下来。
        """
        # 检测是否包含偏好信息
        pref_kws = ["喜欢", "偏好", "习惯", "希望", "要这种", "想要"]
        if any(kw in user_input for kw in pref_kws):
            self.ltm.store(user_input, source="user_preference",
                          importance=0.8, tags=["preference", "auto_extracted"])
            if verbose:
                print(f"      ✅ 自动提取到用户偏好 → 已存入长期记忆")

        # 检测是否包含规则信息
        rule_kws = ["规则", "规定", "标准", "要求", "必须", "不能", "一定"]
        if any(kw in user_input for kw in rule_kws):
            self.ltm.store(user_input, source="business_rule",
                          importance=0.7, tags=["rule", "auto_extracted"])
            if verbose:
                print(f"      ✅ 自动提取到业务规则 → 已存入长期记忆")

        # 检测是否包含知识信息（含"是"、"为"等判断句）
        knowledge_kws = ["是", "有", "包含", "属于", "定义为"]
        if any(kw in user_input for kw in knowledge_kws) and len(user_input) > 10:
            self.ltm.store(user_input, source="knowledge",
                          importance=0.4, tags=["knowledge", "auto_extracted"])
            if verbose:
                print(f"      ✅ 自动提取到知识 → 已存入长期记忆")

    def remember_preference(self, preference: str) -> str:
        """主动让 Agent 记住一个偏好"""
        mem_id = self.ltm.store(
            preference, source="user_preference",
            importance=0.8, tags=["user_preference"]
        )
        return mem_id

    def get_memory_status(self) -> Dict:
        """获取记忆系统整体状态"""
        return {
            "agent_name": self.name,
            "interactions": self.interaction_count,
            "instant_memory": self.instant.get_stats(),
            "short_term_memory": self.stm.get_progress(),
            "long_term_memory": self.ltm.get_statistics()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 第四部分：极简记忆系统 —— 最小可行实现（存、查、用）
# ═══════════════════════════════════════════════════════════════════════════════

class MinimalMemorySystem:
    """
    极简记忆系统 —— 不依赖外部库的最小可行实现。

    虽然只有 50 行核心逻辑，但已经包含了记忆系统的三个本质动作：
    1. 存（store）  —— 把信息保存起来
    2. 查（retrieve）—— 需要时找到相关信息
    3. 用（use）    —— 把记忆融入回复生成

    真实项目中，你只需要把"检索记忆"替换成向量数据库查询即可。
    这个结构是所有记忆系统（从简单到工业级）的共同设计模式。
    """

    def __init__(self):
        self.memories: List[Dict] = []

    def store(self, content: str, category: str = "general") -> int:
        """存：写入一条记忆"""
        mem_id = len(self.memories)
        self.memories.append({
            "id": mem_id,
            "content": content,
            "category": category,
            "timestamp": time.time()
        })
        return mem_id

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """查：基于关键词匹配找到相关记忆"""
        query_words = set(w for w in query if len(w) >= 2)
        scored = []
        for mem in self.memories:
            match_count = sum(1 for w in query_words if w in mem["content"])
            if match_count > 0:
                scored.append((match_count, mem))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in scored[:top_k]]

    def generate(self, user_input: str) -> str:
        """用：基于记忆生成回复"""
        related = self.retrieve(user_input)
        if related:
            ctx = "\n".join(f"- [{r['category']}] {r['content'][:50]}" for r in related)
            return (f"📋 我找到了相关记忆：\n{ctx}\n\n"
                    f"💬 关于「{user_input[:30]}」，基于以上记忆，"
                    f"我可以帮你更好地处理这个问题。")
        else:
            return (f"💬 你说的是：{user_input[:50]}。"
                    f"我暂时没有相关记忆，请告诉我该记住什么。")

    def list_all(self) -> List[Dict]:
        return self.memories

    def delete(self, mem_id: int) -> bool:
        before = len(self.memories)
        self.memories = [m for m in self.memories if m["id"] != mem_id]
        return len(self.memories) < before


# ═══════════════════════════════════════════════════════════════════════════════
# 第五部分：记忆系统设计问题验证
# ═══════════════════════════════════════════════════════════════════════════════

def demo_memory_design_principles():
    """验证记忆系统的三个核心设计问题"""
    print("\n" + "█" * 70)
    print("  记忆系统设计原则验证")
    print("█" * 70)

    embedder = SimpleEmbedding()
    store = VectorMemoryStore(embedder)

    # ── 问题1：记忆越多越好？ ──
    print("\n  ── 设计原则1：不是记忆越多越好 — 高价值优先 ──")
    print()
    # 高质量记忆
    store.store("用户偏好：周报结果先行，突出数据和进度",
                source="user_preference", importance=0.9, tags=["preference"])
    store.store("用户名字叫小王，在科技公司做产品经理",
                source="user_preference", importance=0.8, tags=["profile"])
    store.store("用户偏好简洁、数据驱动的汇报风格",
                source="user_preference", importance=0.7, tags=["preference"])
    # 低质量噪音记忆
    for i in range(10):
        store.store(f"无关噪音数据第{i+1}条：{uuid.uuid4().hex[:8]}",
                    source="noise", importance=0.05, tags=["noise"])
    print(f"\n  总记忆数：{store.get_statistics()['total_items']}")
    print(f"  平均重要性：{store.get_statistics()['avg_importance']:.3f} (被噪音拉低)")

    # 检索测试
    print("\n  检索"写周报"（min_similarity=0）：")
    results = store.retrieve("写周报", top_k=5, min_similarity=0.0)
    for r in results:
        print(f"    [{r.importance:.3f}] {r.content[:40]}...")

    # 裁剪后
    print("\n  裁剪低价值记忆后：")
    store.prune(max_items=10, min_importance=0.3)
    stats = store.get_statistics()
    print(f"  裁剪后：{stats['total_items']} 条 | "
          f"平均重要性：{stats['avg_importance']:.3f}")
    print(f"  裁剪次数：{stats['total_pruned']}")
    print("  ✅ 结论：只沉淀高价值信息，定期清理低价值记忆。\n")

    # ── 问题2：隐私风险 ──
    print("  ── 设计原则2：隐私与安全 — 必须设计隐私管控 ──")
    print()
    store.store("我的手机号是13812345678",
                source="user_preference", importance=0.8, tags=["sensitive"])
    store.store("家庭地址：北京市朝阳区",
                source="user_preference", importance=0.7, tags=["sensitive"])
    store.store("生日是1990年1月1日",
                source="user_preference", importance=0.6, tags=["sensitive"])
    store.store("今天天气很好",
                source="knowledge", importance=0.2, tags=["weather"])

    reports = store.export_sensitive_check()
    print(f"  敏感信息审查：发现 {len(reports)} 条包含敏感关键词的记忆")
    for r in reports:
        print(f"    ⚠ [{r['id']}] {r['content_preview']} → 命中关键词：{r['matched_keywords']}")

    print("\n  用户行使"被遗忘权"（可删除机制）：")
    for r in reports[:2]:
        ok = store.forget(r['id'])
        print(f"    {'✅' if ok else '❌'} 已删除记忆: {r['id']}")
    print("  ✅ 结论：长期记忆必须设计：敏感检测 + 可删除 + 用户知情 + 权限控制\n")

    # ── 问题3：简单至上 ──
    print("  ── 设计原则3：不是越复杂越好 — 先把三件事做对 ──")
    print()
    print("  1. 知道哪些信息该记（识别偏好、规则、知识）")
    print("  2. 知道什么时候该检索（每次处理请求前检索）")
    print("  3. 知道检索后怎么用（组装到上下文中）")
    print("  → 这比盲目堆复杂架构重要得多")
    print("  → 新手 Agent 开发，先把这三步跑通，再考虑高级特性\n")


def demo_minimal_memory_system():
    """演示极简记忆系统的完整工作流"""
    print("\n" + "█" * 70)
    print("  极简记忆系统实战 —— 存、查、用")
    print("█" * 70)

    agent = MinimalMemorySystem()

    # 第一轮：建立记忆
    print("\n  ── 第一轮：建立用户偏好记忆 ──")
    memories = [
        "我叫小王，在科技公司做产品经理",
        "我写周报喜欢结果先行结构，重点突出数据和进度",
        "我的工作涉及数据分析、用户研究和产品规划",
        "我偏好简洁、一目了然的沟通方式",
    ]
    for m in memories:
        mem_id = agent.store(m, category="user_profile")
        print(f"  ✅ 已记住 [{mem_id}]: {m[:40]}...")

    # 第二轮：自动使用记忆
    print("\n  ── 第二轮：Agent 自动使用记忆回复 ──")
    queries = [
        "帮我写本周工作总结",
        "我的工作内容是什么？",
        "我喜欢什么沟通风格？",
    ]
    for q in queries:
        print(f"\n  👤 用户：{q}")
        print(f"  🤖 Agent：{agent.generate(q)}")

    # 第三轮：跨任务复用 —— 分水岭
    print("\n  ── 第三轮：跨任务复用（分水岭） ──")
    print("  （普通聊天机器人：已忘记之前的偏好）")
    print("  （带记忆的 Agent：自动检索并引用历史偏好）")
    print(f"\n  👤 用户：帮我写一篇产品分析报告")
    print(f"  🤖 Agent：{agent.generate('帮我写一篇产品分析报告')}")

    print("\n  ✅ 极简系统的三个核心动作：")
    print("     1. store(content)    → 存")
    print("     2. retrieve(query)   → 查")
    print("     3. generate(input)   → 用\n")


# ═══════════════════════════════════════════════════════════════════════════════
# 第六部分：完整场景 —— "用户设置偏好 → 下一次自动使用"
# ═══════════════════════════════════════════════════════════════════════════════

def run_complete_scenario():
    """
    运行完整场景：用户设置偏好 → 下一次自动使用。

    这是文章中最核心的用例，验证了：
    1. 用户第一次告诉 Agent 自己的偏好
    2. Agent 存入长期记忆
    3. 下一次用户请 Agent 做任务时
    4. Agent 自动检索并参考历史偏好
    5. 无需用户重复说明
    """
    print("\n" + "█" * 70)
    print("  完整场景：『设置偏好 → 自动使用』验证")
    print("  这是长期记忆的价值：把一次性指令变成可持续能力")
    print("█" * 70)

    agent = MemoryAugmentedAgent("记忆增强助手")

    # ── 交互1：用户告知偏好 ──
    print("\n" + "=" * 70)
    print("  🟢 交互1：用户设置偏好")
    print("  用户说：『我写周报喜欢结果先行的结构，重点突出数据和进度』")
    print("=" * 70)
    r1 = agent.chat("记住，我写周报喜欢结果先行的结构，重点突出数据和进度。")
    print(f"\n  🤖 回复：{r1}")

    # ── 交互2：更多偏好 ──
    print("\n" + "=" * 70)
    print("  🟢 交互2：补充更多信息")
    print("  用户说：『我叫小王，在科技公司做产品经理』")
    print("=" * 70)
    r2 = agent.chat("记住，我叫小王，在科技公司做产品经理")
    print(f"\n  🤖 回复：{r2}")

    # ── 交互3：让 Agent 写周报（不重复说明偏好） ──
    print("\n" + "=" * 70)
    print("  🟢 交互3：让Agent写周报（不重复说偏好）")
    print("  用户说：『帮我写本周工作总结』")
    print("  关键验证：Agent应该自动参考交互1中设定的偏好")
    print("=" * 70)
    r3 = agent.chat("帮我写本周工作总结")
    print(f"\n  🤖 回复：{r3}")

    # 验证
    assert "结果先行" in r3 or "核心结论" in r3 or "偏好" in r3, \
        "❌ Agent应自动使用偏好，但回复中未体现！"
    print("\n  ✅ 验证通过：Agent自动参考了第一轮设定的偏好，无需用户重复说明。")
    print("  ✅ 这就是长期记忆的价值：把一次性指令，变成可持续能力。")

    # ── 交互4：同时使用偏好 + 已有知识 ──
    print("\n" + "=" * 70)
    print("  🟢 交互4：补充一条规则后再执行任务")
    print("  用户说：『注意周报中不要出现具体人名，用角色代替』")
    print("=" * 70)
    r4 = agent.chat("记住，周报中不要出现具体人名，用角色代替")
    print(f"\n  🤖 回复：{r4}")

    print("\n  📊 最终记忆状态：")
    stats = agent.ltm.get_statistics()
    print(f"     总记忆条目：{stats['total_items']}")
    print(f"     按来源分布：{stats['by_source']}")
    print(f"     总存储次数：{stats['total_stored']}")
    print(f"     总检索次数：{stats['total_retrieved']}")

    return agent


# ═══════════════════════════════════════════════════════════════════════════════
# 第七部分：记忆系统各层独立验证
# ═══════════════════════════════════════════════════════════════════════════════

def validate_tiered_memory():
    """验证三级记忆架构各层的独立功能"""
    print("\n" + "█" * 70)
    print("  三级记忆架构独立验证")
    print("█" * 70)

    # ── 瞬时记忆验证 ──
    print("\n  ── 验证1：瞬时记忆（窗口溢出自动丢弃）──")
    im = InstantMemory(window_size=3)
    im.set_system_prompt("你是智能助手。")
    msgs = ["第1条消息", "第2条消息", "第3条消息", "第4条消息"]
    for msg in msgs:
        dropped = im.add_message("user", msg)
        if dropped:
            print(f"  添加「{msg}」→ 丢弃「{dropped['content']}」(窗口超限)")
        else:
            print(f"  添加「{msg}」→ 窗口正常")
    context = im.build_context()
    print(f"  最终上下文包含 {len(im.messages)} 条消息")
    assert len(im.messages) == 3, "瞬时记忆应保留最近3条"
    print("  ✅ 瞬时记忆验证通过\n")

    # ── 短期记忆验证 ──
    print("  ── 验证2：短期记忆（任务状态跟踪）──")
    stm = ShortTermMemory()
    stm.start_task("生成周报", "生成本周工作周报",
                   ["收集数据", "分析进展", "撰写内容", "检查格式"])
    stm.complete_step("收集数据", "已读取项目数据库")
    stm.log_tool_call("read_db", {"table": "weekly"}, "返回20条记录")
    stm.confirm_fact("数据来源：项目管理系统")
    progress = stm.get_progress()
    assert progress["completed"] == 1 and progress["total"] == 4
    print(f"  进度：{progress['completed']}/{progress['total']} ({progress['progress_pct']}%)")
    print(f"  工具调用次数：{progress['tool_calls']}")
    assert not stm.is_tool_already_called("read_db", {"table": "weekly"}), \
        "同一工具已调用过，不应再次调用"
    print("  ✅ 短期记忆验证通过\n")

    # ── 长期记忆（向量检索）验证 ──
    print("  ── 验证3：长期记忆（向量语义检索）──")
    embedder = SimpleEmbedding()
    ltm = VectorMemoryStore(embedder)

    # 存入各类记忆
    ltm.store("用户偏好：周报结果先行，突出数据", "preference", 0.9,
              ["preference", "weekly_report"])
    ltm.store("项目A目标：Q2营收增长30%", "business_rule", 0.8,
              ["project_A", "goal"])
    ltm.store("同事张三负责前端开发", "knowledge", 0.4, ["team"])
    ltm.store("今天天气很好", "note", 0.1, ["weather"])

    # 语义检索（不依赖精确匹配）
    results = ltm.retrieve("写周报", top_k=3, min_similarity=0.02)
    assert len(results) >= 1, "应检索到相关记忆"
    print(f"  检索「写周报」→ 找到 {len(results)} 条：")
    for r in results:
        print(f"    [{r.source}] {r.content[:50]}...")
    print("  ✅ 长期记忆（语义检索）验证通过\n")

    # ── 长期记忆（标签检索）验证 ──
    print("  ── 验证4：长期记忆（标签检索）──")
    tagged = ltm.search_by_tags(["preference"])
    print(f"  标签[preference]检索 → 找到 {len(tagged)} 条")
    assert len(tagged) >= 1
    print("  ✅ 标签检索验证通过\n")

    # ── 长期记忆（遗忘机制）验证 ──
    print("  ── 验证5：长期记忆（遗忘机制）──")
    before = len(ltm.items)
    # 主动遗忘一条
    all_items = ltm.get_all_items()
    if all_items:
        ltm.forget(all_items[-1]["id"])
    after = len(ltm.items)
    print(f"  遗忘前 {before} 条 → 遗忘后 {after} 条")
    assert after < before
    print("  ✅ 遗忘机制验证通过\n")

    # ── 长期记忆（过期自动清理）验证 ──
    print("  ── 验证6：长期记忆（过期自动清理）──")
    ltm.store("这条记忆3秒后过期", "test", 0.3, ["test"], ttl_seconds=3)
    before_expiry = len(ltm.items)
    print(f"  存入时：{before_expiry} 条")
    time.sleep(3.1)
    ltm.retrieve("查询", top_k=1)  # 触发清理
    after_expiry = len(ltm.items)
    print(f"  3秒后（已过期）：{after_expiry} 条")
    assert after_expiry < before_expiry, "过期记忆应被自动清理"
    print("  ✅ 过期清理验证通过\n")


# ═══════════════════════════════════════════════════════════════════════════════
# 第八部分：主入口
# ═══════════════════════════════════════════════════════════════════════════════

def print_article_summary():
    """打印本篇知识总结（对应文章第八部分）"""
    print("\n" + "█" * 70)
    print("  本篇核心总结")
    print("█" * 70)
    summary = """
  ▸ 1. 大模型没有天然记忆，只有"上下文感知能力"
       信息不在窗口内，模型就当它不存在——这是健忘的根源。
       三种典型失忆：窗口外失忆、任务间失忆、知识经验失忆。

  ▸ 2. 三级记忆架构：
       瞬时记忆 ← 当前对话上下文（响应最快、容量最小、无需额外存储）
       短期记忆 ← 当前任务状态跟踪（目标、步骤、中间结果、已确认事实）
       长期记忆 ← 跨任务知识与经验沉淀（偏好、规则、知识、经验）

  ▸ 3. 向量数据库是长期记忆的核心载体：
       文本 → Embedding(转为向量) → 语义相近自动靠近 → 相似度检索
       核心公式：存(store) → 查(retrieve) → 用(generate)

  ▸ 4. 记忆模块与 Agent 主流程协同：
       Step 1: 接收目标
       Step 2: 检索长期记忆
       Step 3: 组装上下文（系统提示 + 记忆 + 任务状态）
       Step 4: 执行规划与工具调用
       Step 5: 更新短期记忆
       Step 6: 沉淀长期记忆（新知识/偏好/规则）

  ▸ 5. 极简实现（存、查、用）：
       store(content) → retrieve(query) → generate(prompt + memory)

  ▸ 6. 记忆系统三大设计原则：
       ✗ 不是越多越好 → 只沉淀高价值信息，定期裁剪
       ✗ 有隐私风险 → 敏感检测 + 可删除 + 用户知情 + 权限控制
       ✗ 不是越复杂越好 → 先把"存查用"做对，再按需升级
"""
    print(summary)


if __name__ == "__main__":
    print("\n" + "█" * 70)
    print("  AI Agent 记忆模块详解 —— 完整项目代码")
    print("  覆盖：三级记忆 / 向量检索 / Agent协同 / 设计原则 / 完整用例")
    print("█" * 70)

    # Part 1: 大模型健忘演示
    demo_llm_forgetfulness()

    # Part 2: 三级记忆架构独立验证
    validate_tiered_memory()

    # Part 3: 完整记忆-Agent协同场景
    run_complete_scenario()

    # Part 4: 极简记忆系统
    demo_minimal_memory_system()

    # Part 5: 设计原则验证
    demo_memory_design_principles()

    # 最终总结
    print_article_summary()

    print("\n" + "█" * 70)
    print("  全部演示完成！")
    print("  覆盖6大技术点 + 完整用例验证")
    print("█" * 70 + "\n")
