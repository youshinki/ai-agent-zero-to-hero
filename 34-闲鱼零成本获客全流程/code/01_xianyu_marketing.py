# 第34篇配套代码：闲鱼零成本获客全流程
# 在闲鱼上发布AI服务并获取客户的完整流程
# 运行：python 01_xianyu_marketing.py

# ========== 闲鱼AI服务发布模板 ==========
class XianyuListing:
    """闲鱼商品发布方案"""
    
    @staticmethod
    def generate_title(a_type):
        titles = {
            "custom_agent": "【AI智能体定制】智能客服/知识库问答/自动化办公，按需开发",
            "knowledge_base": "【企业知识库】AI私有知识库搭建，文档问答系统，告别AI幻觉",
            "automation": "【办公自动化】AI自动处理Excel/文档/报告，提效300%",
            "chatbot": "【智能客服】AI客服机器人7x24小时自动回复，接入网站/公众号"
        }
        return titles.get(a_type, "【AI开发】个性化AI应用定制开发")
    
    @staticmethod
    def generate_description(service_type, features, price_range):
        desc = f"""
🚀 {service_type} - AI智能定制开发

💡 我能帮你做什么？
"""
        for f in features:
            desc += f"  ✅ {f}\n"
        
        desc += f"""
💎 服务优势
  ✅ 10年软件开发经验，3年AI应用开发
  ✅ 提供完整代码+部署文档+售后支持
  ✅ 7天免费维护，长期技术支持
  ✅ 不满意可退款（按进度结算）

💰 报价参考
  {price_range}

📌 下单流程
  1️⃣ 私信沟通需求
  2️⃣ 免费出评估方案
  3️⃣ 确认需求后启动
  4️⃣ 分阶段交付验收

⚠️ 注意：不接违法/违规项目
"""
        return desc

# ========== 客户沟通流程 ==========
class CustomerPipeline:
    """客户转化流程"""
    
    def __init__(self):
        self.leads = []
        self.conversations = []
    
    def handle_inquiry(self, customer_name, message):
        """处理客户咨询"""
        response = ""
        if "多少钱" in message or "价格" in message:
            response = f"您好{customer_name}，价格需要根据具体需求来定。方便说下您想实现什么功能吗？我先帮您评估一下。"
        elif "能做" in message or "做过" in message:
            response = f"{customer_name}您好，类似的案例我做过很多（可以发截图）。您具体是什么场景呢？我可以针对性给您出方案。"
        elif "效果" in message or "靠谱" in message:
            response = "可以先做一个小Demo验证效果，满意再继续合作。"
        else:
            response = f"您好{customer_name}，感谢咨询！请描述一下您的需求，我免费出方案和报价。"
        
        self.conversations.append({
            "customer": customer_name,
            "inquiry": message,
            "response": response,
            "time": "now"
        })
        return response
    
    def qualify_lead(self, budget, timeline, clarity):
        """评估客户质量"""
        score = 0
        if budget >= 2000: score += 2
        if timeline <= 14: score += 1
        if clarity >= 7: score += 2
        return {
            "score": score,
            "level": "高意向" if score >= 4 else "中意向" if score >= 2 else "低意向",
            "suggested_action": "立即跟进" if score >= 4 else "持续跟进" if score >= 2 else "先留着"
        }

# ========== 运营执行计划 ==========
def operation_plan():
    return """
📅 闲鱼运营7天计划

【每天必须做】
1️⃣ 早上9点：刷新商品（选择"擦亮"功能）
2️⃣ 下午3点：回复所有未读消息
3️⃣ 晚上8点：查看同行新上架商品，优化自己的描述

【每周必须做】
1️⃣ 更新1-2条商品（不同方向）
2️⃣ 发布3-5个作品展示（成品截图/GitHub链接）
3️⃣ 回复所有评价（好评回复要引导再次下单）

【新手避坑】
1️⃣ 不要直接发联系方式（闲鱼会屏蔽）
2️⃣ 第一单不要高价（建立信用最重要）
3️⃣ 客户问能不能做XX功能时，先确认需求再报价
"""

if __name__ == "__main__":
    print("=" * 60)
    print("🐟 闲鱼零成本获客全流程")
    print("=" * 60)
    
    print("\n📢 商品发布模板")
    print("-" * 40)
    listing = XianyuListing()
    print("标题：", XianyuListing.generate_title("custom_agent"))
    print("\n描述：")
    print(XianyuListing.generate_description(
        "AI智能体定制开发",
        ["OpenAI/GPT-4 API集成", "RAG知识库问答系统", "自动化办公流程", "多轮对话记忆"],
        "基础版：2000-5000元 | 标准版：5000-15000元 | 企业版：15000+元"
    ))
    
    print("\n💬 客户沟通示例")
    print("-" * 40)
    pipeline = CustomerPipeline()
    inquiries = [
        ("张先生", "做个AI客服多少钱？"),
        ("李总", "你能做企业知识库吗？"),
        ("王老板", "效果咋样？靠谱吗？")
    ]
    for name, msg in inquiries:
        print(f"\n客户：{msg}")
        response = pipeline.handle_inquiry(name, msg)
        print(f"回复：{response}")
    
    print("\n📊 客户质量评估")
    print("-" * 40)
    result = pipeline.qualify_lead(budget=5000, timeline=7, clarity=8)
    print(f"得分：{result['score']}")
    print(f"等级：{result['level']}")
    print(f"建议：{result['suggested_action']}")
    
    print(operation_plan())
