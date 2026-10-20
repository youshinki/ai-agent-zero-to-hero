#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第47篇配套完整项目代码 · media_agent.py
赛道2：自媒体内容Agent（全自动日更变现）

五大模块：
  1. 智能选题（垂类关键词 + 热点 + 7/30天清单）
  2. 人设化脚本（5种风格 × 4个平台）
  3. 全自动配图提示词（统一视觉）
  4. 内容自检合规（违规词规避）
  5. 定时批量排期

运行: python media_agent.py
"""

from datetime import datetime, timedelta
from typing import Dict, List


# ======================================================================
# 一、智能选题
# ======================================================================

VERTICAL_KEYWORDS = {
    "AI工具": ["AI效率工具", "提示词技巧", "ChatGPT用法", "AI写作", "AI做图"],
    "职场成长": ["效率提升", "汇报技巧", "时间管理", "副业思维", "沟通表达"],
    "副业变现": ["AI接单", "知识付费", "自媒体变现", "私域运营", "闲鱼获客"],
}

HOT_TEMPLATES = [
    "打工人必看！{kw}的5个隐藏技巧",
    "我用{kw}效率翻倍，亲测有效",
    "{kw}踩坑实录：这3个错误别再犯",
    "零基础也能学会的{kw}方法",
    "{kw}到底值不值得做？真实体验",
]


def generate_topics(niche: str, days: int = 7) -> List[str]:
    kws = VERTICAL_KEYWORDS.get(niche, VERTICAL_KEYWORDS["AI工具"])
    topics = []
    for i in range(days):
        kw = kws[i % len(kws)]
        tpl = HOT_TEMPLATES[i % len(HOT_TEMPLATES)]
        topics.append(tpl.format(kw=kw))
    return topics


# ======================================================================
# 二、人设化脚本
# ======================================================================

PERSONAS = {
    "干货型": {"tone": "信息密度高、条理清晰", "opening": "今天分享一个超实用的方法：",
             "closing": "记得收藏，随时翻出来用。"},
    "吐槽型": {"tone": "幽默、有情绪、接地气", "opening": "我真的服了，居然还有人不知道：",
             "closing": "评论区说说你踩过哪些坑？"},
    "温柔型": {"tone": "亲切、鼓励、陪伴感", "opening": "最近好多姐妹问我：",
             "closing": "慢慢来，我们一起变好呀～"},
    "专业型": {"tone": "严谨、有数据、可信", "opening": "从实践角度看，",
             "closing": "以上结论基于实际测试，供参考。"},
    "接地气型": {"tone": "口语化、生活化", "opening": "说个大实话：",
              "closing": "觉得有用就点个赞，下期继续聊。"},
}

PLATFORM_FORMATS = {
    "小红书": {"length": "300-600字", "style": "emoji + 分段 + 标签",
             "tags": "#AI工具 #效率提升 #副业"},
    "抖音": {"length": "60-90秒口播", "style": "前三秒钩子 + 快节奏",
           "tags": "#AI #干货分享"},
    "视频号": {"length": "1-2分钟", "style": "稳重 + 价值输出", "tags": "#职场 #成长"},
    "公众号": {"length": "1500-2500字", "style": "结构完整 + 小标题", "tags": ""},
}


def generate_script(topic: str, persona: str = "干货型",
                    platform: str = "小红书") -> Dict:
    p = PERSONAS.get(persona, PERSONAS["干货型"])
    fmt = PLATFORM_FORMATS.get(platform, PLATFORM_FORMATS["小红书"])
    body = (f"{p['opening']}{topic}\n\n"
            f"1. 核心方法：把目标拆成可执行的小步骤\n"
            f"2. 关键动作：先跑通最小闭环，再逐步放大\n"
            f"3. 避坑提醒：不要一次贪多，先做透一个场景\n\n"
            f"{p['closing']}")
    return {"topic": topic, "persona": persona, "platform": platform,
            "tone": p["tone"], "format": fmt["style"],
            "length": fmt["length"], "tags": fmt["tags"], "script": body}


# ======================================================================
# 三、配图提示词
# ======================================================================

STYLE_PRESETS = {
    "科技蓝": "科技感，深蓝渐变背景，简洁扁平插画，无文字水印，高清",
    "暖橙成长": "温暖橙色系，手绘插画风，积极向上，无文字，高清",
    "极简黑白": "极简黑白灰，大量留白，杂志排版感，无文字",
}


def generate_cover_prompt(topic: str, style: str = "科技蓝") -> str:
    preset = STYLE_PRESETS.get(style, STYLE_PRESETS["科技蓝"])
    return f"封面主题：{topic}；{preset}；3:4 竖版"


# ======================================================================
# 四、合规自检
# ======================================================================

VIOLATION_WORDS = [
    "最赚钱", "稳赚", "包过", "百分百", "绝对", "第一", "国家级",
    "保证收益", "零风险", "内部渠道", "日入过万", "躺赚",
]

SENSITIVE_REPLACE = {
    "最赚钱": "收益不错",
    "稳赚": "相对稳定",
    "百分百": "大概率",
    "绝对": "通常",
    "第一": "领先",
    "零风险": "风险较低",
    "日入过万": "收益可观",
}


def compliance_check(text: str) -> Dict:
    found = [w for w in VIOLATION_WORDS if w in text]
    fixed = text
    for w in found:
        fixed = fixed.replace(w, SENSITIVE_REPLACE.get(w, "***"))
    return {
        "passed": len(found) == 0,
        "violations": found,
        "fixed_text": fixed,
        "risk": "低" if not found else ("高" if len(found) >= 2 else "中"),
    }


# ======================================================================
# 五、排期
# ======================================================================

def build_schedule(topics: List[str], start: datetime = None,
                   platforms=None) -> List[Dict]:
    start = start or datetime.now()
    platforms = platforms or ["小红书", "抖音", "视频号"]
    rows = []
    for i, t in enumerate(topics):
        day = start + timedelta(days=i)
        rows.append({
            "date": day.strftime("%Y-%m-%d"),
            "platform": platforms[i % len(platforms)],
            "topic": t,
            "time": "19:00",
        })
    return rows


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("📱 赛道2：自媒体内容Agent · 全自动日更演示")
    print("=" * 66)
    
    print("\n[1] 7天选题清单：")
    topics = generate_topics("AI工具", 7)
    for i, t in enumerate(topics, 1):
        print(f"   D{i}：{t}")
    
    print("\n[2] 人设脚本（干货型 / 小红书）：")
    s = generate_script(topics[0], "干货型", "小红书")
    print(f"   风格：{s['tone']}｜格式：{s['format']}｜字数：{s['length']}")
    print(f"   {s['script'][:140].replace(chr(10), ' ')}...")
    
    print("\n[3] 5种人设预览：")
    for persona in PERSONAS:
        print(f"   {persona}：{PERSONAS[persona]['opening']}")
    
    print("\n[4] 封面提示词：")
    print(f"   {generate_cover_prompt(topics[0], '科技蓝')}")
    
    print("\n[5] 合规自检：")
    bad = "这个方法最赚钱，百分百有效，零风险，日入过万！"
    r = compliance_check(bad)
    print(f"   原文：{bad}")
    print(f"   违规词：{r['violations']}（风险：{r['risk']}）")
    print(f"   修正：{r['fixed_text']}")
    
    print("\n[6] 7天排期：")
    for row in build_schedule(topics):
        print(f"   {row['date']} {row['time']} {row['platform']}｜{row['topic'][:18]}...")


if __name__ == "__main__":
    demo()
