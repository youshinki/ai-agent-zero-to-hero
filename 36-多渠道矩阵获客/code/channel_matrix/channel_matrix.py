#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第36篇配套完整项目代码 · channel_matrix.py
多渠道矩阵获客：
  1. B站 / 小红书 / 私域 三渠道策略
  2. 30天内容排期
  3. 获客漏斗计算
  4. 渠道 ROI 对比
  5. 私域运营 SOP

运行: python channel_matrix.py    # 生成矩阵获客方案到 output/
"""

import os

OUTPUT_DIR = "output"


# ======================================================================
# 一、三渠道策略
# ======================================================================

CHANNELS = {
    "B站": {
        "feature": "长视频、技术深度内容、年轻用户",
        "content": [
            "【手把手】30分钟搭建自己的AI智能体",
            "我用AI自动写周报，老板以为我开挂了",
            "AI接单3个月真实经验分享",
            "普通人如何用AI开发副业赚钱",
        ],
        "frequency": "每周2-3条",
        "traffic": "视频简介留公众号/私信获取工具包",
        "convert": "视频引流 → 私域转化 → 接单",
    },
    "小红书": {
        "feature": "图文、种草、决策力强",
        "content": [
            "打工人必备的5个AI工具",
            "AI做PPT有多离谱？我试了试",
            "从0开始做AI副业，我做了什么",
            "用AI一天做了10篇小红书文案",
        ],
        "frequency": "每天1条",
        "traffic": "评论区引导、主页挂联系方式",
        "convert": "种草 → 专业形象 → 咨询 → 接单",
    },
    "私域": {
        "feature": "微信好友/社群/朋友圈，信任沉淀",
        "content": [
            "朋友圈每天1-2条案例/干货",
            "微信群分享AI工具使用技巧",
            "公众号发深度技术文章",
            "私聊维护核心客户",
        ],
        "frequency": "每天1-2条",
        "traffic": "朋友圈留钩子（工具包/资料）",
        "convert": "信任建立 → 需求挖掘 → 方案定制 → 成交",
    },
}


# ======================================================================
# 二、30天内容排期
# ======================================================================

def build_calendar(days: int = 30) -> list:
    bili_topics = CHANNELS["B站"]["content"]
    xhs_topics = CHANNELS["小红书"]["content"]
    moments = ["案例展示（打码）", "AI工具技巧", "行业动态", "客户好评", "周末福利"]
    
    calendar = []
    for day in range(1, days + 1):
        entry = {"day": day, "tasks": []}
        if day % 2 == 1:  # 单号发小红书
            entry["tasks"].append(("小红书", xhs_topics[(day // 2) % len(xhs_topics)]))
        if day % 7 == 1:  # 每周一/隔周发B站
            entry["tasks"].append(("B站", bili_topics[day % len(bili_topics)]))
        entry["tasks"].append(("朋友圈", moments[day % len(moments)]))
        calendar.append(entry)
    return calendar


# ======================================================================
# 三、获客漏斗
# ======================================================================

class Funnel:
    def __init__(self, stages=None):
        self.stages = stages or {
            "曝光": 10000, "点击": 500, "咨询": 50, "报价": 20, "成交": 5,
        }
    
    def conversions(self) -> list:
        items = list(self.stages.items())
        out = []
        for i in range(len(items) - 1):
            (s1, c1), (s2, c2) = items[i], items[i + 1]
            rate = c2 / c1 * 100 if c1 else 0
            out.append({"from": s1, "to": s2,
                        "from_count": c1, "to_count": c2,
                        "rate": f"{rate:.1f}%"})
        return out
    
    def optimize(self, stage: str, target: int) -> dict:
        current = self.stages[stage]
        return {"stage": stage, "current": current, "target": target,
                "growth": f"{(target - current) / current * 100:.1f}%"}


# ======================================================================
# 四、渠道 ROI
# ======================================================================

CHANNEL_ROI = {
    "闲鱼": {"cost": 0, "leads": 15, "note": "零成本，反馈最快"},
    "B站": {"cost": 500, "leads": 8, "note": "内容制作成本（剪辑/封面）"},
    "小红书": {"cost": 300, "leads": 5, "note": "图文制作成本"},
    "知乎": {"cost": 400, "leads": 6, "note": "回答+引流"},
    "私域转介绍": {"cost": 0, "leads": 10, "note": "老客户推荐，转化最高"},
}


def roi_table(close_rate: float = 0.1, price: float = 1200) -> list:
    rows = []
    for name, info in CHANNEL_ROI.items():
        revenue = info["leads"] * close_rate * price
        roi = (revenue - info["cost"]) / info["cost"] * 100 if info["cost"] else float("inf")
        rows.append({
            "channel": name, "cost": info["cost"], "leads": info["leads"],
            "revenue": round(revenue, 2),
            "roi": "∞" if roi == float("inf") else f"{roi:.0f}%",
            "note": info["note"],
        })
    return rows


# ======================================================================
# 五、私域 SOP
# ======================================================================

PRIVATE_SOP = {
    "周一": "客户案例展示（打码保护隐私）",
    "周二": "AI工具推荐/使用技巧",
    "周三": "行业动态/技术分享",
    "周四": "客户好评截图",
    "周五": "周末福利/小工具免费送",
    "周末": "个人思考/生活内容（拉近距离）",
}


# ======================================================================
# 生成方案
# ======================================================================

def build_plan(days: int = 30) -> str:
    out = ["# 多渠道矩阵获客方案\n"]
    
    out.append("## 一、三渠道策略\n")
    for name, info in CHANNELS.items():
        out.append(f"### {name}\n")
        out.append(f"- 平台特征：{info['feature']}")
        out.append(f"- 发布频率：{info['frequency']}")
        out.append(f"- 引流方式：{info['traffic']}")
        out.append(f"- 变现路径：{info['convert']}")
        out.append("- 内容方向：")
        for c in info["content"]:
            out.append(f"  - {c}")
        out.append("")
    
    out.append(f"\n## 二、{days}天内容排期（前14天）\n")
    out.append("| 天 | 渠道 | 内容 |")
    out.append("|----|------|------|")
    for entry in build_calendar(days)[:14]:
        for ch, topic in entry["tasks"]:
            out.append(f"| D{entry['day']} | {ch} | {topic} |")
    
    out.append("\n## 三、获客漏斗\n")
    funnel = Funnel()
    out.append("| 阶段 | 数量 | 转化率 |")
    out.append("|------|------|--------|")
    out.append(f"| 曝光 | {funnel.stages['曝光']} | - |")
    for c in funnel.conversions():
        out.append(f"| {c['to']} | {c['to_count']} | {c['rate']} |")
    
    out.append("\n## 四、渠道 ROI 对比\n")
    out.append("| 渠道 | 投入 | 获客 | 预计收入 | ROI | 说明 |")
    out.append("|------|------|------|----------|-----|------|")
    for r in roi_table():
        out.append(f"| {r['channel']} | ¥{r['cost']} | {r['leads']} | ¥{r['revenue']} | {r['roi']} | {r['note']} |")
    
    out.append("\n## 五、私域朋友圈 SOP\n")
    for day, content in PRIVATE_SOP.items():
        out.append(f"- **{day}**：{content}")
    
    return "\n".join(out)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "矩阵获客方案.md")
    plan = build_plan(30)
    with open(path, "w", encoding="utf-8") as f:
        f.write(plan)
    print("=" * 60)
    print("📱 多渠道矩阵获客方案已生成")
    print("=" * 60)
    print(f"   ✅ {path}（{len(plan)}字）")
