#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第40篇配套完整项目代码 · review_kit.py
商业化全链路复盘：
  1. 项目台账（收入/成本/利润/满意度）
  2. 经营指标汇总
  3. 渠道 ROI 分析
  4. 客户终身价值（CLV）
  5. 获客漏斗
  6. 复盘报告生成

运行: python review_kit.py      # 生成复盘报告到 output/
"""

import os
from datetime import datetime

OUTPUT_DIR = "output"


# ======================================================================
# 一、经营台账
# ======================================================================

class BusinessLedger:
    def __init__(self):
        self.projects = []
        self.channels = {}
    
    def add_project(self, name: str, tier: str, revenue: float,
                    cost: float, satisfaction: float = 4.5):
        profit = revenue - cost
        margin = (profit / revenue * 100) if revenue else 0
        self.projects.append({
            "name": name, "tier": tier, "revenue": revenue, "cost": cost,
            "profit": profit, "margin": round(margin, 1),
            "satisfaction": satisfaction,
        })
    
    def add_channel(self, name: str, cost: float, leads: int):
        self.channels[name] = {"cost": cost, "leads": leads}
    
    # ---------------- 指标 ----------------
    def metrics(self) -> dict:
        total_revenue = sum(p["revenue"] for p in self.projects)
        total_cost = sum(p["cost"] for p in self.projects)
        total_profit = total_revenue - total_cost
        count = len(self.projects) or 1
        return {
            "projects": len(self.projects),
            "revenue": round(total_revenue, 2),
            "cost": round(total_cost, 2),
            "profit": round(total_profit, 2),
            "margin": f"{(total_profit / total_revenue * 100) if total_revenue else 0:.1f}%",
            "avg_price": round(total_revenue / count, 2),
            "avg_satisfaction": round(
                sum(p["satisfaction"] for p in self.projects) / count, 2),
        }
    
    def tier_distribution(self) -> dict:
        dist = {}
        for p in self.projects:
            dist.setdefault(p["tier"], {"count": 0, "revenue": 0})
            dist[p["tier"]]["count"] += 1
            dist[p["tier"]]["revenue"] += p["revenue"]
        return dist
    
    # ---------------- 渠道 ROI ----------------
    def channel_roi(self, close_rate: float = 0.1,
                    avg_price: float = None) -> list:
        avg_price = avg_price or (self.metrics()["avg_price"] or 1200)
        rows = []
        for name, info in self.channels.items():
            revenue = info["leads"] * close_rate * avg_price
            cost = info["cost"]
            roi = ((revenue - cost) / cost * 100) if cost else float("inf")
            rows.append({
                "channel": name, "cost": cost, "leads": info["leads"],
                "revenue": round(revenue, 2),
                "roi": "∞" if roi == float("inf") else f"{roi:.0f}%",
            })
        return sorted(rows, key=lambda x: x["revenue"], reverse=True)


# ======================================================================
# 二、CLV 计算
# ======================================================================

def calculate_clv(initial_order: float, monthly_maintenance: float,
                  months: int, referral_prob: float = 0.2) -> dict:
    maintenance = monthly_maintenance * months
    referral = initial_order * referral_prob
    total = initial_order + maintenance + referral
    return {
        "initial_order": round(initial_order, 2),
        "maintenance": round(maintenance, 2),
        "referral": round(referral, 2),
        "clv": round(total, 2),
        "maintenance_share": f"{(maintenance / total * 100) if total else 0:.0f}%",
        "referral_share": f"{(referral / total * 100) if total else 0:.0f}%",
    }


# ======================================================================
# 三、获客漏斗
# ======================================================================

def funnel_analysis(exposure=10000, clicks=500, inquiries=50,
                    quotes=20, deals=5) -> dict:
    stages = [("曝光", exposure), ("点击", clicks), ("咨询", inquiries),
              ("报价", quotes), ("成交", deals)]
    conversions = []
    for i in range(len(stages) - 1):
        (s1, c1), (s2, c2) = stages[i], stages[i + 1]
        conversions.append({
            "from": s1, "to": s2, "from_count": c1, "to_count": c2,
            "rate": f"{(c2 / c1 * 100) if c1 else 0:.1f}%",
        })
    return {"stages": stages, "conversions": conversions}


# ======================================================================
# 四、复盘报告
# ======================================================================

def build_report(ledger: BusinessLedger, clv: dict) -> str:
    m = ledger.metrics()
    out = ["# AI Agent 接单生意 · 全链路复盘报告",
           f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    
    out.append("## 一、经营概况")
    out.append(f"- 累计项目：{m['projects']} 个")
    out.append(f"- 总收入：¥{m['revenue']}")
    out.append(f"- 总成本：¥{m['cost']}")
    out.append(f"- 总利润：¥{m['profit']}")
    out.append(f"- 平均利润率：{m['margin']}")
    out.append(f"- 平均客单价：¥{m['avg_price']}")
    out.append(f"- 平均满意度：{m['avg_satisfaction']}/5\n")
    
    out.append("## 二、项目明细")
    out.append("| 项目 | 等级 | 收入 | 成本 | 利润 | 利润率 | 满意度 |")
    out.append("|------|------|------|------|------|--------|--------|")
    for p in ledger.projects:
        out.append(f"| {p['name']} | {p['tier']} | ¥{p['revenue']} | ¥{p['cost']} "
                   f"| ¥{p['profit']} | {p['margin']}% | {p['satisfaction']} |")
    
    out.append("\n## 三、项目等级分布")
    for tier, info in ledger.tier_distribution().items():
        out.append(f"- {tier}：{info['count']} 个，收入 ¥{info['revenue']}")
    
    out.append("\n## 四、渠道 ROI")
    out.append("| 渠道 | 投入 | 获客 | 预计收入 | ROI |")
    out.append("|------|------|------|----------|-----|")
    for r in ledger.channel_roi():
        out.append(f"| {r['channel']} | ¥{r['cost']} | {r['leads']} "
                   f"| ¥{r['revenue']} | {r['roi']} |")
    
    out.append("\n## 五、客户终身价值（CLV）")
    out.append(f"- 首单收入：¥{clv['initial_order']}")
    out.append(f"- 维护收入：¥{clv['maintenance']}（{clv['maintenance_share']}）")
    out.append(f"- 推荐收入：¥{clv['referral']}（{clv['referral_share']}）")
    out.append(f"- **CLV 合计：¥{clv['clv']}**")
    
    out.append("\n## 六、关键结论")
    out.append("1. 高客单价项目利润率高，但获客周期长")
    out.append("2. 运维托管是长期稳定现金流")
    out.append("3. 老客户推荐是最高效获客渠道")
    out.append("4. 技术壁垒决定溢价空间，持续积累案例与文档")
    
    return "\n".join(out)


# ======================================================================
# 演示数据 + 生成
# ======================================================================

def build_demo_ledger() -> BusinessLedger:
    ledger = BusinessLedger()
    ledger.add_project("企业客服知识库", "L2", 1800, 300, 5)
    ledger.add_project("个人资料问答", "L1", 800, 150, 4)
    ledger.add_project("文档自动答疑", "L2", 1200, 250, 5)
    ledger.add_project("多部门知识库", "L3", 3500, 900, 4)
    ledger.add_project("API对接调试", "L1", 800, 100, 4)
    ledger.add_channel("闲鱼", 0, 15)
    ledger.add_channel("B站", 500, 8)
    ledger.add_channel("小红书", 300, 5)
    ledger.add_channel("私域转介绍", 0, 10)
    return ledger


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ledger = build_demo_ledger()
    clv = calculate_clv(1800, 500, 12)
    report = build_report(ledger, clv)
    path = os.path.join(OUTPUT_DIR, "商业化复盘报告.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    print("=" * 60)
    print("📊 商业化全链路复盘报告已生成")
    print("=" * 60)
    print(f"   ✅ {path}（{len(report)}字）")
