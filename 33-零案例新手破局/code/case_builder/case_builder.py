#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第33篇配套完整项目代码 · case_builder.py
零案例新手破局：零成本自建3套商用级落地案例

  案例1：小微企业制度知识库（通用万金油）
  案例2：产品售后问答知识库（高需求高客单）
  案例3：个人/自媒体内容知识库（引流爆款）

配套：案例包装（演示视频脚本 + 标准化文案）+ 首单破零策略
==========================================================================
"""

import os

OUTPUT_DIR = "cases_output"


# ======================================================================
# 一、三套标杆案例定义
# ======================================================================

CASES = {
    "case1_企业制度知识库": {
        "name": "小微企业制度知识库",
        "scene": "所有小微企业、工作室、个体户通用",
        "pain_points": [
            "员工制度、考勤、报销规则分散，新人反复问",
            "HR 每天重复回答相同问题，效率低",
            "制度更新后，旧文档仍在流传，口径不一致",
        ],
        "capabilities": [
            "私有化部署，企业资料不出内网",
            "批量解析 Word/PDF/TXT 制度文件",
            "精准问答：入职、考勤、报销、岗位职责",
            "无资料如实提示，杜绝编造",
            "商用干净输出，可直接给员工使用",
        ],
        "value": [
            "HR 答疑工作量下降 80%",
            "新人培训周期缩短一半",
            "制度口径统一，减少争议",
        ],
        "docs": {
            "员工手册.txt": "员工手册\n考勤规则：每日9:00-18:00，迟到超过30分钟扣半天工资。\n"
                        "请假流程：提前1天在OA提交申请，直属上级审批。\n"
                        "入职流程：提交身份证、学历证明、体检报告，签署劳动合同。",
            "报销制度.txt": "报销制度\n差旅报销：交通、住宿、餐饮按标准报销，需提供发票。\n"
                        "报销流程：填写报销单→直属上级审批→财务复核→3个工作日到账。\n"
                        "报销时限：费用发生后30天内提交，逾期不予受理。",
            "岗位职责.txt": "岗位职责\n产品经理：负责需求分析、产品规划、跨部门协调。\n"
                        "研发工程师：负责功能开发、代码评审、技术文档。\n"
                        "运营专员：负责内容运营、活动策划、数据复盘。",
        },
        "demo_questions": [
            ("考勤规则是什么？", "考勤规则：每日9:00-18:00，迟到超过30分钟扣半天工资。"),
            ("报销怎么走流程？", "报销流程：填写报销单→直属上级审批→财务复核→3个工作日到账。"),
            ("入职需要准备什么？", "入职流程：提交身份证、学历证明、体检报告，签署劳动合同。"),
        ],
    },
    "case2_产品售后知识库": {
        "name": "产品售后问答知识库",
        "scene": "电商商家、实体店铺、设备厂家、服务行业",
        "pain_points": [
            "客服重复回答产品参数、保修、退换货问题",
            "夜间/节假日无人值守，客户流失",
            "新人客服培训慢，回答口径不一致",
        ],
        "capabilities": [
            "产品参数、使用教程、售后政策一库查询",
            "7×24 小时自动答疑，替代部分人工客服",
            "标准化回答口径，新人快速上手",
            "多格式资料批量入库，持续更新",
        ],
        "value": [
            "客服人力成本下降 50%",
            "夜间咨询自动承接，减少客户流失",
            "售后口径统一，减少纠纷",
        ],
        "docs": {
            "产品参数.txt": "产品参数\n产品名称：智能蓝牙耳机\n蓝牙版本：5.3\n续航：单次8小时，配合充电仓30小时\n"
                        "防水等级：IPX5\n支持协议：AAC/SBC",
            "售后政策.txt": "售后政策\n7天无理由退货：不影响二次销售可退，运费自理。\n"
                        "质量问题：15天内包换，1年内保修。\n退款时效：签收后3-5个工作日原路退回。",
            "使用教程.txt": "使用教程\n开机：长按电源键3秒。\n配对：手机蓝牙搜索'SmartEar-01'点击连接。\n"
                        "充电：放入充电仓自动充电，指示灯常亮表示充满。",
        },
        "demo_questions": [
            ("耳机续航多久？", "续航：单次8小时，配合充电仓30小时。"),
            ("质量问题怎么换？", "质量问题：15天内包换，1年内保修。"),
            ("怎么配对手机？", "配对：手机蓝牙搜索'SmartEar-01'点击连接。"),
        ],
    },
    "case3_个人内容知识库": {
        "name": "个人/自媒体内容知识库",
        "scene": "博主、自媒体、知识付费、个人IP",
        "pain_points": [
            "粉丝重复提问，私信回不过来",
            "历史干货散落在各平台，难以检索",
            "个人时间被答疑占满，无法专注创作",
        ],
        "capabilities": [
            "行业干货、教程笔记、常见问题统一入库",
            "粉丝自助答疑，7×24 可用",
            "知识点快速检索，提升粉丝体验",
            "打造个人 AI 工具 IP，增强信任",
        ],
        "value": [
            "私信答疑时间下降 90%",
            "粉丝体验提升，转化率提高",
            "个人 IP 增加 AI 工具标签，提升溢价",
        ],
        "docs": {
            "AI工具教程.txt": "AI工具教程\n提示词技巧：角色+任务+格式+约束四段式。\n"
                          "常用工具：ChatGPT、Claude、DeepSeek、Midjourney。\n"
                          "避坑：不要一次给太多要求，分步迭代效果更好。",
            "副业经验.txt": "副业经验\n第一步：选定一个细分场景（知识库/客服/内容）。\n"
                        "第二步：做出可演示的成品案例。\n第三步：低价破零，积累口碑后再提价。",
            "常见问题.txt": "常见问题\n问：零基础能学会吗？\n答：跟着系列教程，先跑通Demo再逐步进阶。\n"
                        "问：需要多少启动成本？\n答：主要是API费用，可先用低成本模型。",
        },
        "demo_questions": [
            ("提示词怎么写更好？", "提示词技巧：角色+任务+格式+约束四段式。"),
            ("副业第一步做什么？", "第一步：选定一个细分场景（知识库/客服/内容）。"),
            ("零基础能学会吗？", "答：跟着系列教程，先跑通Demo再逐步进阶。"),
        ],
    },
}


# ======================================================================
# 二、案例构建器
# ======================================================================

class CaseBuilder:
    def __init__(self):
        self.case_dirs = {}
    
    def build_case(self, case_key: str) -> dict:
        case = CASES[case_key]
        case_dir = os.path.join(OUTPUT_DIR, case_key)
        data_dir = os.path.join(case_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # 写入示例资料
        for name, content in case["docs"].items():
            with open(os.path.join(data_dir, name), "w", encoding="utf-8") as f:
                f.write(content)
        
        # 生成案例说明
        readme = self._generate_readme(case)
        with open(os.path.join(case_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme)
        
        # 生成演示问答记录
        demo = self._generate_demo(case)
        with open(os.path.join(case_dir, "demo_qa.md"), "w", encoding="utf-8") as f:
            f.write(demo)
        
        self.case_dirs[case_key] = case_dir
        return {"key": case_key, "dir": case_dir,
                "docs": len(case["docs"]), "questions": len(case["demo_questions"])}
    
    @staticmethod
    def _generate_readme(case: dict) -> str:
        pains = "\n".join(f"- {x}" for x in case["pain_points"])
        caps = "\n".join(f"- {x}" for x in case["capabilities"])
        vals = "\n".join(f"- {x}" for x in case["value"])
        return f"""# {case['name']} · 案例说明

## 项目背景
{case['scene']}

**痛点：**
{pains}

## 项目能力
{caps}

## 项目价值
{vals}

## 交付内容
- 私有知识库系统（源码 + 部署文档）
- 示例资料库（{len(case['docs'])}份文档已入库）
- 使用手册 + 售后方案
- 演示问答记录（demo_qa.md）
"""
    
    @staticmethod
    def _generate_demo(case: dict) -> str:
        lines = [f"# {case['name']} · 演示问答", ""]
        for i, (q, a) in enumerate(case["demo_questions"], 1):
            lines.append(f"**Q{i}：{q}**")
            lines.append(f"A{i}：{a}")
            lines.append("")
        return "\n".join(lines)
    
    def build_all(self) -> list:
        return [self.build_case(k) for k in CASES]


# ======================================================================
# 三、案例包装
# ======================================================================

class CasePackaging:
    @staticmethod
    def video_script(case_name: str) -> str:
        return f"""# {case_name} · 演示视频脚本（3-5分钟）

| 时间 | 画面 | 配音/字幕 |
|------|------|-----------|
| 0:00-0:30 | 系统启动、首页界面 | 这是为企业搭建的私有AI知识库，资料全部本地存储 |
| 0:30-1:30 | 批量入库过程（拖入文档→自动解析） | 支持Word/PDF/TXT批量导入，自动清洗去重 |
| 1:30-3:00 | 多场景精准问答演示 | 基于私有资料精准作答，无资料如实提示 |
| 3:00-4:00 | 干净输出 + 隐私拦截演示 | 商用级排版，敏感问题自动拦截 |
| 4:00-4:30 | 成本与稳定性数据 | 缓存节流、智能路由，稳定低成本运行 |
| 4:30-5:00 | 交付清单/售后方案 | 全套交付文档，7天免费售后 |
"""
    
    @staticmethod
    def copy_template(case: dict) -> str:
        return f"""# {case['name']} · 接单文案（四段式）

## 一、项目背景
{case['pain_points'][0]}
{case['pain_points'][1]}

## 二、项目能力
{chr(10).join('- ' + c for c in case['capabilities'])}

## 三、项目价值
{chr(10).join('- ' + v for v in case['value'])}

## 四、适配客户
{case['scene']}
"""
    
    @staticmethod
    def first_order_strategy() -> str:
        return """# 新手首单破零策略

## 定价逻辑
- 第一单：500-1500 元（积累案例与口碑，快速成交）
- 第二单：2000-5000 元（有案例背书，正常报价）
- 第三单起：5000+ 元（按项目复杂度报价）

## 成交节奏
1. 用 3 套自建案例做展示素材
2. 客户咨询时先问需求、再出方案、最后报价
3. 首单可提供"先做小功能验证，满意再继续"
4. 交付时附全套文档，建立专业形象
5. 主动请求好评/案例授权（脱敏），形成口碑闭环

## 避坑
- 不接需求不清、预算过低的单
- 不承诺无法实现的功能
- 不无限免费改需求（按交付清单与售后方案执行）
"""


# ======================================================================
# 入口
# ======================================================================

def build_all_cases():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    builder = CaseBuilder()
    results = builder.build_all()
    
    # 生成包装素材
    for case_key, case in CASES.items():
        case_dir = os.path.join(OUTPUT_DIR, case_key)
        with open(os.path.join(case_dir, "视频脚本.md"), "w", encoding="utf-8") as f:
            f.write(CasePackaging.video_script(case["name"]))
        with open(os.path.join(case_dir, "接单文案.md"), "w", encoding="utf-8") as f:
            f.write(CasePackaging.copy_template(case))
    
    with open(os.path.join(OUTPUT_DIR, "首单破零策略.md"), "w", encoding="utf-8") as f:
        f.write(CasePackaging.first_order_strategy())
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("📦 构建 3 套商用级案例")
    print("=" * 60)
    results = build_all_cases()
    for r in results:
        print(f"   ✅ {r['key']}：{r['docs']}份文档，{r['questions']}个演示问答 → {r['dir']}")
    print(f"\n包装素材与破零策略已生成到 {OUTPUT_DIR}/")
