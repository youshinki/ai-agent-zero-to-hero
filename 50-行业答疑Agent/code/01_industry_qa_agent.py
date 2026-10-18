# 第50篇配套代码：行业答疑Agent
# 垂直领域专属变现赛道
# 运行：python 01_industry_qa_agent.py

# ========== 行业知识库 ==========
class IndustryKnowledgeBase:
    """行业知识库"""
    
    def __init__(self, industry_name):
        self.industry = industry_name
        self.knowledge = {}
        self.faqs = []
    
    def add_knowledge(self, topic, content, tags=None):
        """添加知识条目"""
        self.knowledge[topic] = {
            "content": content,
            "tags": tags or [],
            "related_questions": []
        }
    
    def add_faq(self, question, answer, category="general"):
        """添加FAQ"""
        self.faqs.append({
            "question": question,
            "answer": answer,
            "category": category
        })
    
    def search(self, query):
        """搜索知识库"""
        results = []
        for topic, info in self.knowledge.items():
            if query in topic or any(query in tag for tag in info["tags"]):
                results.append({
                    "topic": topic,
                    "content": info["content"][:200],
                    "relevance": 0.9
                })
        return sorted(results, key=lambda x: x["relevance"], reverse=True)[:3]

# ========== 行业问答Agent ==========
class IndustryQAAgent:
    """行业问答Agent"""
    
    def __init__(self, industry):
        self.industry = industry
        self.kb = IndustryKnowledgeBase(industry)
        self._init_default_knowledge()
    
    def _init_default_knowledge(self):
        """初始化默认知识"""
        default_kb = {
            "AI": {
                "机器学习": "机器学习是AI的一个分支，让计算机从数据中学习...",
                "深度学习": "深度学习使用多层神经网络处理复杂模式...",
                "自然语言处理": "NLP让计算机理解、生成人类语言..."
            },
            "法律": {
                "合同法": "合同法是调整合同关系的法律规范的总称...",
                "知识产权": "知识产权包括专利、商标、著作权等...",
                "劳动法": "劳动法保护劳动者的合法权益..."
            },
            "医疗": {
                "常见病": "常见疾病包括感冒、发烧、高血压等...",
                "药物知识": "药物使用需遵医嘱，注意禁忌症...",
                "健康管理": "定期体检、合理饮食、适量运动..."
            },
            "金融": {
                "投资理财": "投资理财需根据风险承受能力选择产品...",
                "保险知识": "保险是风险转移的重要工具...",
                "税务规划": "合理税务规划可有效降低税负..."
            }
        }
        
        if self.industry in default_kb:
            for topic, content in default_kb[self.industry].items():
                self.kb.add_knowledge(topic, content, [self.industry, topic])
    
    def answer(self, question):
        """回答问题"""
        # 搜索FAQ
        for faq in self.kb.faqs:
            if faq["question"] in question:
                return faq["answer"]
        
        # 搜索知识库
        results = self.kb.search(question)
        if results:
            return f"根据行业知识库，找到相关答案：\n{results[0]['content']}"
        
        return f"关于「{question}」的问题，建议咨询专业{self.industry}人士。我可以帮您查找更多相关资料。"
    
    def get_industry_info(self):
        """获取行业信息"""
        info = {
            "AI": {"trend": "AI正在重塑各行各业", "demand": "极高", "avg_price": "10000-30000"},
            "法律": {"trend": "法律AI辅助工具需求增长", "demand": "高", "avg_price": "8000-20000"},
            "医疗": {"trend": "医疗AI诊断辅助发展迅速", "demand": "高", "avg_price": "15000-50000"},
            "金融": {"trend": "金融科技持续创新", "demand": "高", "avg_price": "20000-50000"}
        }
        return info.get(self.industry, {"trend": "新兴领域", "demand": "中", "avg_price": "5000-15000"})

if __name__ == "__main__":
    print("=" * 60)
    print("💼 行业答疑Agent - 垂直领域专属变现")
    print("=" * 60)
    
    industries = ["AI", "法律", "医疗", "金融"]
    
    for industry in industries:
        print(f"\n{'=' * 50}")
        print(f"🔷 {industry}行业答疑Agent")
        print(f"{'=' * 50}")
        
        agent = IndustryQAAgent(industry)
        
        # 添加行业FAQ
        agent.kb.add_faq(
            f"{industry}行业需要什么资质？",
            f"从事{industry}行业需要相关资质证书和许可..."
        )
        
        info = agent.get_industry_info()
        print(f"  趋势：{info['trend']}")
        print(f"  需求：{info['demand']}")
        print(f"  平均报价：{info['avg_price']}")
        
        print("\n  测试问答：")
        test_questions = [
            f"什么是{['机器学习','合同法','常见病','投资理财'][industries.index(industry)]}？",
            f"{industry}行业需要什么资质？"
        ]
        for q in test_questions:
            print(f"  Q：{q}")
            print(f"  A：{agent.answer(q)[:100]}...")
    
    print("\n" + "=" * 60)
    print("💰 变现路径")
    print("=" * 60)
    print("""
  1️⃣ 行业知识库搭建：5000-20000元
  2️⃣ 行业答疑API接口：3000-8000元/月
  3️⃣ 专属行业Agent定制：10000-50000元
  4️⃣ 知识付费课程：99-999元/套
  5️⃣ 企业咨询服务：500-2000元/小时
""")
