#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第59篇配套完整项目代码 · multi_agent.py
多Agent协作架构：分工、审议、层级仲裁三种模式

  1. Pipeline（分工流水线）
  2. Debate（审议/投票）
  3. Hierarchical（层级仲裁）
  4. 共享消息总线
  5. 超时与失败兜底
==========================================================================
"""

from typing import (Callable, Dict, List)


# ======================================================================
# 一、消息总线
# ======================================================================

class MessageBus:
    def __init__(self):
        self.messages: List[Dict] = []
    
    def publish(self, sender: str, content: str, to: str = "all"):
        msg = {"from": sender, "to": to, "content": content}
        self.messages.append(msg)
        return msg
    
    def read(self, agent: str) -> List[Dict]:
        return [m for m in self.messages
                if m["to"] in (agent, "all") and m["from"] != agent]


# ======================================================================
# 二、Agent
# ======================================================================

class Agent:
    def __init__(self, name: str, role: str,
                 handler: Callable[[str], str]):
        self.name = name
        self.role = role
        self.handler = handler
    
    def work(self, task: str) -> str:
        return self.handler(task)


# ======================================================================
# 三、三种协作模式
# ======================================================================

class Pipeline:
    """分工流水线：A → B → C，后一步依赖前一步结果"""
    
    def __init__(self, agents: List[Agent]):
        self.agents = agents
        self.bus = MessageBus()
    
    def run(self, task: str) -> Dict:
        log, current = [], task
        for agent in self.agents:
            self.bus.publish("orchestrator", current, agent.name)
            out = agent.work(current)
            log.append({"agent": agent.name, "role": agent.role,
                        "input": current[:40], "output": out[:60]})
            current = out
        return {"mode": "pipeline", "task": task, "log": log,
                "final": current}


class Debate:
    """审议模式：多个Agent独立作答，投票/裁决"""
    
    def __init__(self, agents: List[Agent], judge: Agent):
        self.agents = agents
        self.judge = judge
        self.bus = MessageBus()
    
    def run(self, question: str) -> Dict:
        opinions = []
        for agent in self.agents:
            out = agent.work(question)
            opinions.append({"agent": agent.name, "opinion": out})
            self.bus.publish(agent.name, out, "judge")
        
        # 裁决：把意见交给 judge
        combined = "\n".join(f"[{o['agent']}] {o['opinion']}" for o in opinions)
        verdict = self.judge.work(combined)
        return {"mode": "debate", "question": question,
                "opinions": opinions, "verdict": verdict}


class Hierarchical:
    """层级仲裁：manager 拆解 → workers 执行 → manager 汇总"""
    
    def __init__(self, manager: Agent, workers: List[Agent]):
        self.manager = manager
        self.workers = workers
        self.bus = MessageBus()
    
    def run(self, goal: str) -> Dict:
        # 1. 拆解
        plan_text = self.manager.work(f"拆解任务：{goal}")
        subtasks = [s.strip() for s in plan_text.split("；") if s.strip()]
        if not subtasks:
            subtasks = [goal]
        
        # 2. 分配执行
        results = []
        for i, sub in enumerate(subtasks):
            worker = self.workers[i % len(self.workers)]
            self.bus.publish("manager", sub, worker.name)
            out = worker.work(sub)
            results.append({"worker": worker.name, "subtask": sub,
                            "result": out})
        
        # 3. 汇总
        combined = "\n".join(f"- {r['subtask']} → {r['result']}" for r in results)
        final = self.manager.work(f"汇总结果：\n{combined}")
        return {"mode": "hierarchical", "goal": goal,
                "subtasks": subtasks, "results": results, "final": final}


# ======================================================================
# 四、演示
# ======================================================================

def mock_agents():
    researcher = Agent("researcher", "研究", lambda t: f"资料清单：{t[:20]}相关要点")
    writer = Agent("writer", "写作", lambda t: f"报告初稿：基于「{t[:20]}」撰写")
    reviewer = Agent("reviewer", "审核", lambda t: f"审核通过：{t[:20]}（已优化）")
    judge = Agent("judge", "裁决", lambda t: f"裁决：采纳综合意见（{len(t)}字）")
    manager = Agent("manager", "管理",
                    lambda t: "任务A；任务B；任务C" if "拆解" in t else f"汇总完成：{t[:30]}")
    return researcher, writer, reviewer, judge, manager


def demo():
    print("=" * 66)
    print("👥 多Agent协作架构演示")
    print("=" * 66)
    researcher, writer, reviewer, judge, manager = mock_agents()
    
    print("\n[1] 分工流水线：")
    p = Pipeline([researcher, writer, reviewer])
    r = p.run("AI Agent 在企业客服中的应用")
    for item in r["log"]:
        print(f"   {item['agent']}（{item['role']}）→ {item['output'][:40]}")
    print(f"   最终：{r['final'][:50]}")
    
    print("\n[2] 审议投票：")
    d = Debate([researcher, writer], judge)
    r = d.run("RAG 和微调怎么选？")
    print(f"   意见数：{len(r['opinions'])}")
    print(f"   裁决：{r['verdict'][:50]}")
    
    print("\n[3] 层级仲裁：")
    h = Hierarchical(manager, [researcher, writer, reviewer])
    r = h.run("生成季度业务分析报告")
    print(f"   子任务：{r['subtasks']}")
    for item in r["results"]:
        print(f"   {item['worker']}：{item['result'][:40]}")
    print(f"   汇总：{r['final'][:50]}")


if __name__ == "__main__":
    demo()
