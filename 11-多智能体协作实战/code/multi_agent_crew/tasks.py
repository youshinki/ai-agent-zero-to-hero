#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第11篇配套完整项目代码 · tasks.py
定义每个Agent的任务（文章第七章）

关键原则：每个Task都必须写清楚 expected_output
==========================================================================
"""

from config import USE_MOCK
from agents import researcher, writer, reviewer

if USE_MOCK:
    from crew_mock import Task
else:
    from crewai import Task


# 任务1：研究员收集资料（{topic} 为运行时变量）
research_task = Task(
    description="针对主题“{topic}”，收集相关背景、核心观点、关键数据和应用案例，整理成资料清单。",
    expected_output="一份结构化资料清单，包含背景、核心观点、关键数据、应用案例四部分。",
    agent=researcher,
)

# 任务2：撰稿人写报告（上下文自动接收上一个任务输出）
writing_task = Task(
    description="基于研究员提供的资料，撰写一份完整中文报告。报告包含标题、引言、正文、结论四个部分。",
    expected_output="一篇结构完整、逻辑清晰、语言正式的中文报告。",
    agent=writer,
)

# 任务3：审核员审核优化
review_task = Task(
    description="审核报告，检查是否存在信息遗漏、逻辑断层、表达不清或结构问题，并输出最终优化版。",
    expected_output="一份经过审核优化后的最终报告，并附修改说明。",
    agent=reviewer,
)

ALL_TASKS = [research_task, writing_task, review_task]


if __name__ == "__main__":
    for t in ALL_TASKS:
        print(f"[{t.agent.role}] {t.expected_output}")
