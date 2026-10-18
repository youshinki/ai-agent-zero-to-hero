# 第48篇配套代码：电商AI顾问赛道
# 智能客服店铺答疑变现
# 运行：python 01_ecommerce_agent.py

# ========== 电商AI客服 ==========
class EcommerceAgent:
    """电商AI顾问"""
    
    def __init__(self, store_name="智能店铺"):
        self.store_name = store_name
        self.knowledge_base = {}
        self.conversations = []
    
    def add_product(self, product_id, name, price, specs, stock):
        """添加商品信息"""
        self.knowledge_base[product_id] = {
            "name": name,
            "price": price,
            "specs": specs,
            "stock": stock
        }
    
    def answer_question(self, question, customer_info=None):
        """回答客户问题"""
        question_lower = question.lower()
        
        # 意图识别
        if "价格" in question_lower or "多少钱" in question_lower:
            return self._handle_price_query(question)
        elif "库存" in question_lower or "有货" in question_lower:
            return self._handle_stock_query(question)
        elif "规格" in question_lower or "参数" in question_lower:
            return self._handle_specs_query(question)
        elif "退货" in question_lower or "退款" in question_lower:
            return self._handle_return_query()
        elif "物流" in question_lower or "快递" in question_lower:
            return self._handle_shipping_query()
        elif "优惠" in question_lower or "折扣" in question_lower:
            return self._handle_discount_query()
        else:
            return self._handle_general_query(question)
    
    def _handle_price_query(self, question):
        """处理价格查询"""
        for pid, product in self.knowledge_base.items():
            if product["name"] in question:
                return f"💰 {product['name']}当前售价 ¥{product['price']}，现在下单还有优惠哦！"
        return f"亲，我们店商品价格在 {min(p['price'] for p in self.knowledge_base.values())}-{max(p['price'] for p in self.knowledge_base.values())} 元之间，您想看哪一款？"
    
    def _handle_stock_query(self, question):
        for pid, product in self.knowledge_base.items():
            if product["name"] in question:
                if product["stock"] > 0:
                    return f"✅ {product['name']} 有货！库存充足，可以放心下单~"
                else:
                    return f"😅 抱歉，{product['name']} 暂时缺货，预计3天后补货，您可以先收藏~"
        return "大部分商品都有货，您可以看看具体哪一款~"
    
    def _handle_specs_query(self, question):
        for pid, product in self.knowledge_base.items():
            if product["name"] in question:
                return f"📋 {product['name']} 规格：{product['specs']}"
        return "您说的是哪一款商品呢？我帮您查一下~"
    
    def _handle_return_query(self):
        return """📦 退换货政策：
- 7天无理由退货（不影响二次销售）
- 质量问题包邮退换
- 非质量问题运费自理
- 退款将在3-5个工作日原路返回

有需要可以直接联系我处理~"""
    
    def _handle_shipping_query(self):
        return "🚚 默认发顺丰快递，下单后24小时内发货，一般1-3天到货~"
    
    def _handle_discount_query(self):
        return "🎉 当前活动：满200减20，满500减50！现在下单最划算~"
    
    def _handle_general_query(self, question):
        return f"亲，您好！有什么可以帮您的吗？想看看我们家 {'、'.join(p['name'] for p in self.knowledge_base.values())} 中的哪一款呢？"
    
    def record_conversation(self, customer, question, answer):
        """记录对话（用于后续优化）"""
        self.conversations.append({
            "customer": customer,
            "question": question,
            "answer": answer,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        })

# ========== 客服评价 ==========
class CustomerFeedback:
    """客户反馈分析"""
    
    @staticmethod
    def analyze_satisfaction(ratings):
        avg = sum(ratings) / len(ratings) if ratings else 0
        if avg >= 4.5: return "非常满意"
        elif avg >= 4.0: return "满意"
        elif avg >= 3.0: return "一般"
        else: return "需改进"

if __name__ == "__main__":
    print("=" * 60)
    print("🛒 电商AI顾问赛道")
    print("=" * 60)
    
    agent = EcommerceAgent("智能好物店")
    agent.add_product("P001", "智能蓝牙耳机", 299, "蓝牙5.3/降噪/续航30h", 100)
    agent.add_product("P002", "无线充电宝", 149, "20000mAh/快充/轻薄", 50)
    agent.add_product("P003", "智能手表", 599, "心率监测/运动模式/IP68防水", 30)
    
    questions = [
        "这个耳机多少钱？",
        "充电宝有货吗？",
        "智能手表什么规格？",
        "怎么退货？",
        "发什么快递？",
        "有优惠吗？"
    ]
    
    for q in questions:
        print(f"\n客户：{q}")
        answer = agent.answer_question(q)
        print(f"客服：{answer}")
    
    print("\n📊 客服评价分析")
    print("-" * 40)
    feedback = CustomerFeedback()
    ratings = [5, 4, 5, 4, 5, 3]
    print(f"  评分：{ratings}")
    print(f"  满意度：{feedback.analyze_satisfaction(ratings)}")
    print(f"  平均分：{sum(ratings)/len(ratings):.1f}")
