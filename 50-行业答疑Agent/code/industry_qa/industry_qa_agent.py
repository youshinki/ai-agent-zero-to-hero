#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第50篇配套完整项目代码 · industry_qa_agent.py
赛道5：行业答疑Agent（垂直领域专属变现）

  1. 多行业知识库（AI/法律/医疗/金融/教育）
  2. 专家人设与免责声明
  3. FAQ 匹配与知识检索
  4. 线索捕获（咨询/联系意图）
  5. 行业报价与交付

运行: python industry_qa_agent.py
"""

import re
from typing import Dict, List, Optional


# ======================================================================
# 一、行业知识库
# ======================================================================

INDUSTRY_KB = {
    "法律": {
        "expert": "资深法律顾问",
        "disclaimer": "以上内容仅供参考，不构成正式法律意见，具体案件请咨询执业律师。",
        "entries": {
            "劳动合同": "劳动合同应包含：用人单位信息、劳动者信息、合同期限、工作内容、劳动报酬、社会保险等条款。",
            "试用期": "劳动合同期限3个月以上不满1年的，试用期不得超过1个月；1年以上不满3年的，不得超过2个月；3年以上固定期限和无固定期限的，不得超过6个月。",
            "竞业限制": "竞业限制期限不得超过2年，用人单位需按月支付经济补偿。",
        },
        "faq": [
            ("公司不给签劳动合同怎么办？", "可向劳动监察部门投诉，或申请劳动仲裁，主张未签合同期间的双倍工资。"),
            ("被违法辞退怎么维权？", "收集证据（通知、聊天记录、考勤），申请劳动仲裁，主张违法解除赔偿金（2N）。"),
        ],
        "price": "8000-20000元（知识库+答疑系统）",
    },
    "医疗": {
        "expert": "健康管理顾问",
        "disclaimer": "以上内容仅供健康科普参考，不能替代医生诊断，如有不适请及时就医。",
        "entries": {
            "高血压": "高血压患者应低盐饮食、规律运动、按时服药、定期监测血压。",
            "体检项目": "常规体检包括血常规、尿常规、肝肾功能、血脂血糖、心电图、腹部超声等。",
            "疫苗接种": "疫苗接种需按免疫程序进行，接种后留观30分钟。",
        },
        "faq": [
            ("血压多少算高？", "诊室血压≥140/90mmHg通常诊断为高血压，需多次测量确认。"),
            ("体检前要注意什么？", "体检前一天清淡饮食、避免饮酒，空腹8-12小时。"),
        ],
        "price": "10000-30000元（健康知识库）",
    },
    "金融": {
        "expert": "理财规划顾问",
        "disclaimer": "以上内容不构成投资建议，投资有风险，决策需谨慎。",
        "entries": {
            "资产配置": "资产配置应结合风险承受能力，分散投资于现金、债券、股票、保险等。",
            "基金定投": "基金定投通过定期定额投资平滑成本，适合长期投资。",
            "保险规划": "保险规划优先配置医疗险、重疾险、意外险，再考虑理财型保险。",
        },
        "faq": [
            ("新手怎么开始理财？", "先建立应急资金（3-6个月开支），再根据风险偏好配置低风险产品。"),
            ("年化收益多少合理？", "收益与风险匹配，过高收益往往伴随高风险，警惕承诺保本高息。"),
        ],
        "price": "15000-40000元（金融知识库）",
    },
    "AI": {
        "expert": "AI应用顾问",
        "disclaimer": "以上内容基于当前技术实践，具体方案需结合业务评估。",
        "entries": {
            "RAG": "RAG（检索增强生成）通过检索私有资料增强生成，显著降低幻觉。",
            "Agent": "AI Agent 具备规划、记忆、工具调用、反思能力，可自主完成复杂任务。",
            "微调": "微调适合有大量标注数据、需要特定风格或领域的场景，成本高于RAG。",
        },
        "faq": [
            ("企业怎么做AI落地？", "先从高频、低风险场景切入（知识库问答/客服），验证效果后再扩展。"),
            ("RAG和微调怎么选？", "知识频繁更新选RAG；需要固定风格/领域能力且数据充足选微调。"),
        ],
        "price": "10000-30000元（企业AI知识库）",
    },
}


# ======================================================================
# 二、行业答疑 Agent
# ======================================================================

class IndustryQAAgent:
    def __init__(self, industry: str):
        if industry not in INDUSTRY_KB:
            raise ValueError(f"暂不支持行业：{industry}")
        self.industry = industry
        self.kb = INDUSTRY_KB[industry]
        self.history: List[dict] = []
        self.leads = 0
    
    def _match_faq(self, question: str) -> Optional[str]:
        for q, a in self.kb["faq"]:
            # 关键词重叠匹配
            q_chars = set(q) & set(question)
            if len(q_chars) >= 4:
                return a
        return None
    
    def _search_entries(self, question: str) -> Optional[str]:
        best, score = None, 0.0
        for topic, content in self.kb["entries"].items():
            s = len(set(question) & set(topic + content)) / max(len(set(question)), 1)
            if s > score:
                best, score = content, s
        return best if score >= 0.25 else None
    
    def ask(self, question: str) -> Dict:
        # 线索捕获
        if any(k in question for k in ["多少钱", "怎么收费", "联系方式", "合作", "定制"]):
            self.leads += 1
            answer = (f"我们提供{self.industry}行业专属答疑系统定制，参考报价：{self.kb['price']}。"
                      f"可以留下您的需求，我帮您安排方案沟通。")
            return {"type": "lead", "answer": answer}
        
        answer = self._match_faq(question) or self._search_entries(question)
        if not answer:
            answer = (f"关于「{question}」，我暂时无法给出准确答复。"
                      f"建议咨询专业{self.kb['expert']}。")
            return {"type": "fallback", "answer": answer}
        
        self.history.append({"q": question, "a": answer})
        return {"type": "answer", "expert": self.kb["expert"],
                "answer": answer, "disclaimer": self.kb["disclaimer"]}


# ======================================================================
# 演示
# ======================================================================

def demo():
    print("=" * 66)
    print("💼 赛道5：行业答疑Agent · 演示")
    print("=" * 66)
    
    for industry in ["法律", "医疗", "金融", "AI"]:
        print(f"\n{'─' * 60}")
        print(f"🔷 {industry}行业（{INDUSTRY_KB[industry]['expert']}）")
        agent = IndustryQAAgent(industry)
        questions = [
            INDUSTRY_KB[industry]["faq"][0][0],
            "你们怎么收费？",
        ]
        for q in questions:
            r = agent.ask(q)
            print(f"   问：{q}")
            print(f"   答：{r['answer'][:80]}")
            if "disclaimer" in r:
                print(f"   ⚠️ {r['disclaimer'][:40]}...")
        print(f"   💰 参考报价：{INDUSTRY_KB[industry]['price']}")


if __name__ == "__main__":
    demo()
