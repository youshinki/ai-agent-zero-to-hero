#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第37篇配套完整项目代码 · pricing_kit.py
项目分级与报价体系：
  1. L1-L4 四级项目分级
  2. 5 维项目评估
  3. 工时核算 + 风险预留
  4. 增值项单独计价
  5. 需求变更管控 + 报价话术

运行: python pricing_kit.py     # 生成报价手册到 output/
"""

import os

OUTPUT_DIR = "output"


# ======================================================================
# 一、四级项目分级
# ======================================================================

TIERS = {
    "L1 轻量基础版": {
        "scenarios": ["个人小需求", "简单知识库体验"],
        "features": ["基础RAG系统", "文档批量入库", "操作手册", "7天BUG修复"],
        "hours": "0.5-1个工作日",
        "price": 800,
        "deliverables": ["基础RAG系统", "文档批量入库", "操作手册", "7天BUG修复"],
        "pay_terms": "一次性或 50%+50%",
    },
    "L2 商用标准版": {
        "scenarios": ["小微企业内部知识库", "员工资料查询", "基础客服问答"],
        "features": [
            "全格式文档解析", "文本清洗", "重排序检索", "Token压缩",
            "成本优化模块", "少量界面微调", "无复杂权限系统",
        ],
        "hours": "1-3个工作日",
        "price": 1200,
        "deliverables": ["全套商用源码", "知识库全套能力", "交付清单", "完整文档", "7天BUG修复"],
        "pay_terms": "50% 预付 + 50% 验收",
    },
    "L3 深度定制版": {
        "scenarios": ["商家多角色使用", "企业多部门知识库"],
        "features": [
            "多用户权限管理", "独立账号", "对接第三方系统（企微/飞书）",
            "定制前端页面", "专属业务逻辑开发", "需要修改底层代码",
        ],
        "hours": "3-8个工作日",
        "price": 2500,
        "deliverables": ["定制开发完整系统", "源码", "部署文档", "测试报告", "15天BUG维护"],
        "pay_terms": "50% 预付 + 50% 验收",
    },
    "L4 大型企业项目": {
        "scenarios": ["中大型企业", "多知识库隔离", "完整后台管理"],
        "features": [
            "多租户隔离", "日志审计", "高并发优化", "对接企业业务系统",
            "持续迭代开发", "可配套月度运维",
        ],
        "hours": "8个工作日以上（分阶段）",
        "price": 6000,
        "deliverables": ["分阶段交付", "完整工程文档", "测试用例", "上线部署", "专属运维方案"],
        "pay_terms": "按里程碑分阶段收款",
    },
}

# 增值项（不打包进基础套餐）
ADDONS = {
    "大批量扫描文档OCR解析": "按文档数量计价",
    "服务器部署、环境搭建": "300元起",
    "月度运维托管服务": "500元/月起",
    "新增独立功能模块": "按预估工时报价",
}


# ======================================================================
# 二、5 维项目评估
# ======================================================================

class ProjectEvaluator:
    """五维评估 → 项目等级"""
    
    DIMENSIONS = {
        "文档规模与类型": {
            "low": "少量txt/md", "mid": "数十份常见格式", "high": "大量扫描件/PDF图片/表格",
        },
        "定制开发需求": {
            "low": "纯使用现成成品", "mid": "少量界面微调", "high": "新功能/改底层/定制UI",
        },
        "第三方对接需求": {
            "low": "无", "mid": "简单API", "high": "企微/飞书/小程序/多系统",
        },
        "部署环境要求": {
            "low": "本地单机", "mid": "云服务器", "high": "高可用/高并发/私有化集群",
        },
        "售后与运维要求": {
            "low": "7天BUG修复", "mid": "15天维护", "high": "长期驻场/持续迭代",
        },
    }
    
    SCORE = {"low": 1, "mid": 2, "high": 3}
    
    @classmethod
    def evaluate(cls, ratings: dict) -> dict:
        total = sum(cls.SCORE[v] for v in ratings.values())
        if total <= 7:
            tier = "L1 轻量基础版"
        elif total <= 10:
            tier = "L2 商用标准版"
        elif total <= 12:
            tier = "L3 深度定制版"
        else:
            tier = "L4 大型企业项目"
        return {"total_score": total, "tier": tier,
                "details": ratings}


# ======================================================================
# 三、工时核算与报价
# ======================================================================

class QuoteCalculator:
    def __init__(self, day_rate: float = 800):
        self.day_rate = day_rate  # 期望单日收入
    
    def quote(self, tier: str, workdays: float,
              reuse_ratio: float = 0.0, addons=None,
              risk_buffer: float = 0.2) -> dict:
        """报价 = 工时 × 日薪 × (1-复用率) × (1+风险预留) + 增值项"""
        base_hours_cost = workdays * self.day_rate
        after_reuse = base_hours_cost * (1 - reuse_ratio)
        risk = after_reuse * risk_buffer
        addon_cost = 0
        for a in (addons or []):
            addon_cost += 300 if "部署" in a else 0  # 简化：部署300起
        total = after_reuse + risk + addon_cost
        
        tier_price = TIERS[tier]["price"]
        return {
            "tier": tier,
            "workdays": workdays,
            "day_rate": self.day_rate,
            "base_cost": round(base_hours_cost, 2),
            "reuse_ratio": f"{reuse_ratio * 100:.0f}%",
            "after_reuse": round(after_reuse, 2),
            "risk_buffer": f"{risk_buffer * 100:.0f}%",
            "risk_cost": round(risk, 2),
            "addon_cost": addon_cost,
            "calculated_total": round(total, 2),
            "tier_reference_price": tier_price,
            "suggested_price": round(max(total, tier_price), 2),
        }


# ======================================================================
# 四、需求变更管控与话术
# ======================================================================

CHANGE_RULES = [
    "开发前锁定交付需求清单",
    "原有需求范围内BUG修复：免费（含在售后内）",
    "新增功能/修改原有逻辑：需求变更，重新评估工时单独报价",
    "无补充约定的新增需求，乙方有权拒绝开发",
]

QUOTE_SCRIPTS = {
    "客户嫌贵": (
        "咱们这个属于{tier}，交付的不是简单Demo，包含文档清洗、RAG重排、"
        "溯源引用、API成本优化全套商用能力，附带完整源码和交付文档。"
        "后期资料增量更新、长期使用稳定，避免廉价Demo的幻觉和崩溃问题。"
    ),
    "客户预算有限": (
        "如果预算有限，可以降级到 L1 基础版，减少部分定制功能来降低预算，"
        "而不是在同等项目上直接砍价。"
    ),
    "需求变更": (
        "本次报价对应的是咱们确认好的需求清单。如果后续新增功能，"
        "我这边评估工时，给您单独报一个新增项目的价格，这样项目周期可控，"
        "不会影响原定交付进度。"
    ),
}


# ======================================================================
# 五、生成报价手册
# ======================================================================

def build_manual() -> str:
    out = ["# 项目分级与报价体系手册\n"]
    out.append("## 一、四级项目分级\n")
    for name, info in TIERS.items():
        out.append(f"### {name}（参考价 ¥{info['price']}）")
        out.append(f"- 适用：{'、'.join(info['scenarios'])}")
        out.append(f"- 需求：{'、'.join(info['features'])}")
        out.append(f"- 工时：{info['hours']}")
        out.append(f"- 交付：{'、'.join(info['deliverables'])}")
        out.append(f"- 付款：{info['pay_terms']}\n")
    
    out.append("## 二、5维评估定级\n")
    for dim, levels in ProjectEvaluator.DIMENSIONS.items():
        out.append(f"- **{dim}**：低={levels['low']}｜中={levels['mid']}｜高={levels['high']}")
    
    out.append("\n## 三、增值项\n")
    for k, v in ADDONS.items():
        out.append(f"- {k}：{v}")
    
    out.append("\n## 四、需求变更规则\n")
    for r in CHANGE_RULES:
        out.append(f"- {r}")
    
    out.append("\n## 五、报价话术\n")
    for name, text in QUOTE_SCRIPTS.items():
        out.append(f"### {name}\n{text}\n")
    
    out.append("\n## 六、报价避坑\n")
    for tip in [
        "大单分阶段收款（预付50%，验收结清尾款）",
        "不口头评估工时，需求/范围/报价全部文字确认",
        "不为接单低估工作量",
        "区分BUG修复与新增功能",
        "不同渠道统一分级报价",
    ]:
        out.append(f"- {tip}")
    return "\n".join(out)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    manual = build_manual()
    path = os.path.join(OUTPUT_DIR, "报价手册.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(manual)
    print("=" * 60)
    print("💰 项目分级与报价手册已生成")
    print("=" * 60)
    print(f"   ✅ {path}（{len(manual)}字）")
