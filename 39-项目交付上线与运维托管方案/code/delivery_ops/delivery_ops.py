#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第39篇配套完整项目代码 · delivery_ops.py
项目交付上线与运维托管：
  1. 上线检查清单（功能/部署/安全/文档）
  2. 运维托管套餐（基础/标准/高级）
  3. 运维排期（日/周/月）
  4. 托管收入与 LTV 计算
  5. 交付报告生成

运行: python delivery_ops.py    # 生成交付报告到 output/
"""

import os
from datetime import datetime

OUTPUT_DIR = "output"


# ======================================================================
# 一、上线检查清单
# ======================================================================

CHECKLIST = {
    "功能验收": [
        "所有功能按需求实现",
        "边界情况处理正常",
        "错误提示友好",
        "性能满足要求",
    ],
    "部署检查": [
        "服务器环境配置完成",
        "数据库/向量库初始化完成",
        "域名解析正确（如适用）",
        "环境变量正确配置",
        "服务可正常启动",
    ],
    "安全检查": [
        "API密钥不硬编码",
        "接口权限控制",
        "敏感数据脱敏",
        "日志不含敏感信息",
        "隐私拦截生效",
    ],
    "文档交付": [
        "部署文档（环境/步骤/配置）",
        "使用手册（功能/操作）",
        "API文档（接口/参数/示例）",
        "运维手册（监控/备份/故障处理）",
        "交付清单（签字确认）",
    ],
}


def build_checklist(project_name: str) -> str:
    out = [f"# {project_name} 上线检查清单",
           f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    for category, items in CHECKLIST.items():
        out.append(f"## {category}")
        for item in items:
            out.append(f"- [ ] {item}")
        out.append("")
    out.append("## 验收签字\n")
    out.append("- 交付方：________________  日期：__________")
    out.append("- 接收方：________________  日期：__________")
    return "\n".join(out)


# ======================================================================
# 二、运维托管套餐
# ======================================================================

PLANS = {
    "基础托管": {
        "price": "1000-2000元/月",
        "includes": ["服务器监控（每日检查）", "数据备份（每周）",
                     "安全更新", "工作日4小时响应"],
        "suitable": "个人项目/C级项目",
    },
    "标准托管": {
        "price": "3000-5000元/月",
        "includes": ["7×24小时监控", "每日数据备份", "安全更新+性能优化",
                     "故障2小时响应", "每月功能小优化(2小时)", "季度健康报告"],
        "suitable": "中小企业/A级项目",
    },
    "高级托管": {
        "price": "8000-15000元/月",
        "includes": ["7×24实时监控+告警", "实时备份+异地容灾", "安全加固+渗透测试",
                     "故障30分钟响应", "每月8小时功能优化", "月度健康报告+优化建议",
                     "专属技术支持群", "SLA 99.9%"],
        "suitable": "大型企业/S级项目",
    },
}


# ======================================================================
# 三、运维排期
# ======================================================================

SCHEDULE = {
    "每日": [
        ("09:00", "检查服务状态"),
        ("10:00", "检查API调用量"),
        ("14:00", "检查错误日志"),
        ("17:00", "生成日报"),
    ],
    "每周": [
        ("周一", "数据库/向量库备份"),
        ("周三", "磁盘清理"),
        ("周五", "性能评估"),
    ],
    "每月": [
        ("第1周", "安全更新"),
        ("第2周", "知识库质量评估"),
        ("第3周", "客户回访"),
        ("第4周", "月度报告"),
    ],
}


# ======================================================================
# 四、收入与 LTV
# ======================================================================

def calculate_revenue(client_count: int, avg_monthly_fee: float) -> dict:
    monthly = client_count * avg_monthly_fee
    return {
        "clients": client_count,
        "avg_monthly_fee": avg_monthly_fee,
        "monthly_revenue": monthly,
        "annual_revenue": monthly * 12,
        "ltv_3y_per_client": avg_monthly_fee * 36,
    }


# ======================================================================
# 五、交付报告
# ======================================================================

def build_handover_report(project_name: str, client: str,
                          features: list, tier: str = "L2 商用标准版") -> str:
    out = [f"# {project_name} · 交付报告\n"]
    out.append(f"- 客户：{client}")
    out.append(f"- 项目等级：{tier}")
    out.append(f"- 交付日期：{datetime.now().strftime('%Y-%m-%d')}\n")
    
    out.append("## 一、交付功能清单")
    for f in features:
        out.append(f"- [x] {f}")
    
    out.append("\n## 二、上线检查结论")
    out.append("- [x] 功能验收通过")
    out.append("- [x] 部署检查通过")
    out.append("- [x] 安全检查通过")
    out.append("- [x] 文档交付完成")
    
    out.append("\n## 三、售后与运维")
    out.append("- 免费售后：交付后 7 天（功能 BUG 修复）")
    out.append("- 可选托管：基础/标准/高级（见运维方案）")
    out.append("- 响应方式：工作日 4 小时内 / 非工作日 12 小时内")
    
    out.append("\n## 四、后续迭代建议")
    out.append("1. 持续补充企业文档，提升覆盖率")
    out.append("2. 定期做问答质量评分，针对性优化文档")
    out.append("3. 可按需扩展多用户权限、第三方系统对接")
    
    return "\n".join(out)


# ======================================================================
# 一键生成
# ======================================================================

def generate_all(project_name="企业私有知识库", client="XX科技",
                 features=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    features = features or ["文档批量入库", "语义检索问答", "溯源引用", "商用干净输出"]
    
    files = {
        "01_上线检查清单.md": build_checklist(project_name),
        "02_运维托管方案.md": "# 运维托管方案\n\n" + "\n".join(
            f"## {name}（{info['price']}）\n" +
            "\n".join(f"- {x}" for x in info["includes"]) +
            f"\n- 适合：{info['suitable']}\n"
            for name, info in PLANS.items()
        ),
        "03_运维排期.md": "# 运维排期\n\n" + "\n".join(
            f"## {period}\n" + "\n".join(f"- {t} {task}" for t, task in items)
            for period, items in SCHEDULE.items()
        ),
        "04_交付报告.md": build_handover_report(project_name, client, features),
    }
    paths = []
    for name, content in files.items():
        path = os.path.join(OUTPUT_DIR, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        paths.append(path)
    return paths


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 生成交付与运维文档")
    print("=" * 60)
    paths = generate_all()
    for p in paths:
        print(f"   ✅ {p}（{os.path.getsize(p)}字节）")
