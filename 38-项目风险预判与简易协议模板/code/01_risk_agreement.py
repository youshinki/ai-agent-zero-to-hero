# 第38篇配套代码：项目风险预判与简易协议模板
# 规避交付纠纷，保护开发者权益
# 运行：python 01_risk_agreement.py

from datetime import datetime

# ========== 项目风险评估 ==========
class RiskAssessor:
    """项目风险预判"""
    
    RISK_FACTORS = {
        "需求不明确": {"level": "高", "mitigation": "书面确认需求文档，签字确认"},
        "客户频繁改需求": {"level": "高", "mitigation": "约定免费修改次数，超出收费"},
        "数据获取困难": {"level": "中", "mitigation": "提前确认数据格式和获取方式"},
        "技术可行性": {"level": "中", "mitigation": "前期做技术验证，确认可行再启动"},
        "第三方依赖": {"level": "中", "mitigation": "提前测试API可用性，准备备选方案"},
        "交付验收标准": {"level": "高", "mitigation": "明确验收标准和验收流程"}
    }
    
    @staticmethod
    def assess_project(requirements, third_party_deps, timeline):
        """综合评估项目风险"""
        risks = []
        risk_score = 0
        
        if not requirements or len(requirements) < 5:
            risks.append({"risk": "需求不明确", "score": 3})
            risk_score += 3
        
        if third_party_deps:
            risks.append({"risk": f"依赖{len(third_party_deps)}个第三方服务", "score": 2})
            risk_score += 2
        
        if timeline < 7:
            risks.append({"risk": "工期过短", "score": 2})
            risk_score += 2
        
        return {
            "risk_score": risk_score,
            "level": "高风险" if risk_score >= 5 else "中风险" if risk_score >= 3 else "低风险",
            "details": risks,
            "suggestion": "建议签正式合同" if risk_score >= 5 else "建议有书面确认" if risk_score >= 3 else "正常推进"
        }

# ========== 简易协议模板 ==========
class AgreementTemplate:
    """项目协议模板"""
    
    @staticmethod
    def generate_simple_agreement(
        developer="开发者姓名",
        client="客户姓名",
        project_name="AI智能体开发项目",
        total_price=10000,
        deposit_ratio=0.5,
        features=None,
        timeline_days=15
    ):
        features = features or ["智能问答功能", "知识库管理", "基础管理后台"]
        
        deposit = total_price * deposit_ratio
        final_payment = total_price - deposit
        
        agreement = f"""
# {project_name} 项目合作协议

## 一、合作双方
- 开发方（乙方）：{developer}
- 委托方（甲方）：{client}
- 签订日期：{datetime.now().strftime('%Y年%m月%d日')}

## 二、项目内容
"""
        for i, feat in enumerate(features, 1):
            agreement += f"{i}. {feat}\n"

        agreement += f"""
## 三、费用与支付
- 项目总金额：¥{total_price}
- 首期款（{int(deposit_ratio*100)}%）：¥{int(deposit)}（签约时支付）
- 尾款（{int((1-deposit_ratio)*100)}%）：¥{int(final_payment)}（验收后支付）

## 四、交付周期
- 预计工期：{timeline_days}个工作日
- 交付物：完整源代码 + 部署文档 + 使用手册

## 五、验收标准
1. 功能满足需求文档中的描述
2. 无明显bug（不影响正常使用）
3. 部署后可正常运行

## 六、双方责任
- 甲方：提供需求文档、及时反馈、按时付款
- 乙方：按时交付、保证质量、提供{timeline_days}天免费维护

## 七、知识产权
- 项目源码归乙方所有，甲方获得永久使用权
- 乙方有权将项目用于案例展示（需脱敏）

## 八、免责条款
1. 因第三方API变更导致的问题不属乙方责任
2. 甲方自行修改代码导致的问题不在维护范围内
3. 不可抗力因素导致延期不属违约

## 九、协议变更
- 任何变更需双方书面确认
- 新增功能需另签补充协议

---
双方确认无误后签字生效
"""
        return agreement
    
    @staticmethod
    def change_request_form():
        """需求变更确认单"""
        return """
# 需求变更确认单

项目名称：_______________
变更编号：CR-{date}-{num}

## 变更内容
原需求：_______________
新需求：_______________

## 影响评估
- 工作量增加：___天
- 费用增加：___元
- 工期待延：___天

## 确认
- 开发方签字：___________  日期：___________
- 委托方签字：___________  日期：___________
"""

# ========== 纠纷处理流程 ==========
class DisputeHandler:
    """纠纷处理方案"""
    
    @staticmethod
    def handle_dispute(dispute_type):
        handlers = {
            "需求理解不一致": [
                "立即截图保存所有沟通记录",
                "重新确认需求文档",
                "友好协商达成共识"
            ],
            "交付质量不满意": [
                "列出具体问题清单",
                "区分bug和需求变更",
                "bug免费修复，变更重新报价"
            ],
            "尾款拖欠": [
                "先友好提醒",
                "发正式催款函",
                "停止服务/代码回退"
            ],
            "客户要求退款": [
                "按进度结算已完成的工时",
                "扣除已投入的资源成本",
                "签署终止协议"
            ]
        }
        return handlers.get(dispute_type, ["双方冷静沟通", "寻求第三方调解"])

if __name__ == "__main__":
    print("=" * 60)
    print("⚠️ 项目风险预判与协议模板")
    print("=" * 60)
    
    print("\n📊 风险评估")
    print("-" * 40)
    result = RiskAssessor.assess_project(
        requirements=["智能问答", "知识库"],
        third_party_deps=["OpenAI API", "ChromaDB"],
        timeline=10
    )
    print(f"风险评分：{result['risk_score']}")
    print(f"风险等级：{result['level']}")
    print(f"建议：{result['suggestion']}")
    for d in result['details']:
        print(f"  ⚠️ {d['risk']}")
    
    print("\n📝 简易协议")
    print("-" * 40)
    agreement = AgreementTemplate.generate_simple_agreement()
    print(agreement[:800] + "\n...")
    
    print("\n⚖️ 纠纷处理")
    print("-" * 40)
    dispute = DisputeHandler()
    for issue, steps in dispute.handle_dispute("尾款拖欠").items() if False else \
        [("尾款拖欠", ["先友好提醒", "发正式催款函", "停止服务"])]:
        print(f"  {issue}：")
        for s in steps:
            print(f"    • {s}")
