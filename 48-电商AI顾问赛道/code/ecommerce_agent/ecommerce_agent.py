#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第48篇配套完整项目代码 · ecommerce_agent.py
赛道3：电商AI顾问（智能客服店铺答疑变现）

  1. 商品知识库（参数/价格/库存）
  2. 意图识别（售前/售后/物流/退换/优惠）
  3. 标准化回复（统一口径）
  4. 人工转接（超边界问题）
  5. 订单查询（模拟）

运行: python ecommerce_agent.py
"""

from typing import Dict, List, Optional


# ======================================================================
# 一、商品知识库
# ======================================================================

class ProductKB:
    def __init__(self):
        self.products: Dict[str, dict] = {}
    
    def add(self, sku: str, name: str, price: float, specs: dict,
            stock: int, warranty: str = ""):
        self.products[sku] = {
            "name": name, "price": price, "specs": specs,
            "stock": stock, "warranty": warranty,
        }
    
    def find_by_name(self, text: str) -> Optional[dict]:
        for sku, p in self.products.items():
            name = p["name"]
            if name in text or sku.lower() in text.lower():
                return {"sku": sku, **p}
            # 反向匹配：查询词是商品名子串（如"耳机"→"智能蓝牙耳机"）
            if len(text) >= 2 and text in name:
                return {"sku": sku, **p}
            # 关键词匹配：商品名中的2字词出现在查询中
            if any(name[i:i+2] in text for i in range(len(name) - 1)):
                return {"sku": sku, **p}
        return None
    
    def all_products(self) -> List[dict]:
        return [{"sku": k, **v} for k, v in self.products.items()]


# ======================================================================
# 二、意图识别
# ======================================================================

INTENTS = {
    "price": ["多少钱", "价格", "什么价", "便宜"],
    "spec": ["参数", "规格", "配置", "尺寸", "续航", "材质"],
    "stock": ["有货", "库存", "还有吗", "缺货"],
    "warranty": ["保修", "质保", "售后", "坏了", "维修"],
    "return": ["退货", "退款", "换货", "七天无理由"],
    "logistics": ["发货", "快递", "物流", "多久到", "包邮"],
    "discount": ["优惠", "活动", "满减", "券"],
}


def detect_intent(text: str) -> str:
    for intent, kws in INTENTS.items():
        if any(k in text for k in kws):
            return intent
    return "general"


# ======================================================================
# 三、客服 Agent
# ======================================================================

class EcommerceAgent:
    def __init__(self, kb: ProductKB):
        self.kb = kb
        self.memory: List[dict] = []
        self.escalated = 0
    
    def reply(self, message: str) -> Dict:
        intent = detect_intent(message)
        product = self.kb.find_by_name(message)
        
        if intent == "price" and product:
            answer = (f"亲，{product['name']} 当前售价 ¥{product['price']}，"
                      f"现在下单还有优惠哦～")
        elif intent == "spec" and product:
            specs = "、".join(f"{k}：{v}" for k, v in product["specs"].items())
            answer = f"亲，{product['name']} 的规格是：{specs}。"
        elif intent == "stock" and product:
            if product["stock"] > 0:
                answer = f"亲，{product['name']} 有货，库存充足，可以放心下单～"
            else:
                answer = f"亲，{product['name']} 暂时缺货，预计3天补货，可以先收藏哦～"
        elif intent == "warranty":
            w = product["warranty"] if product and product["warranty"] else "1年质保，15天包换"
            answer = f"亲，我们提供 {w}。质量问题包邮退换，请放心购买～"
        elif intent == "return":
            answer = ("亲，支持7天无理由退货（不影响二次销售），质量问题包邮退换；"
                      "退款3-5个工作日原路退回～")
        elif intent == "logistics":
            answer = "亲，默认发顺丰快递，下单后24小时内发货，一般1-3天到货～"
        elif intent == "discount":
            answer = "亲，当前活动：满200减20，满500减50，现在下单最划算～"
        else:
            # 超边界 → 转人工
            self.escalated += 1
            answer = "这个问题我需要帮您转接人工客服，请稍等～"
        
        record = {"message": message, "intent": intent,
                  "product": product["name"] if product else None,
                  "answer": answer}
        self.memory.append(record)
        return record


# ======================================================================
# 四、订单查询（模拟）
# ======================================================================

ORDERS = {
    "ORD-001": {"status": "已发货", "product": "智能蓝牙耳机", "eta": "明天送达"},
    "ORD-002": {"status": "待发货", "product": "无线充电宝", "eta": "24小时内发出"},
}


def query_order(order_id: str) -> str:
    o = ORDERS.get(order_id)
    if not o:
        return "未查询到该订单，请核对订单号～"
    return f"订单 {order_id}：{o['product']}，状态：{o['status']}，{o['eta']}。"


# ======================================================================
# 演示
# ======================================================================

def demo():
    kb = ProductKB()
    kb.add("P001", "智能蓝牙耳机", 299,
           {"蓝牙": "5.3", "续航": "30小时", "防水": "IPX5"}, 100,
           warranty="1年质保，15天包换")
    kb.add("P002", "无线充电宝", 149,
           {"容量": "20000mAh", "快充": "22.5W", "重量": "380g"}, 0)
    
    agent = EcommerceAgent(kb)
    
    print("=" * 66)
    print("🛒 赛道3：电商AI顾问 · 智能客服演示")
    print("=" * 66)
    questions = [
        "智能蓝牙耳机多少钱？",
        "耳机续航多久？",
        "充电宝有货吗？",
        "保修多久？",
        "怎么退货？",
        "什么时候发货？",
        "有优惠吗？",
        "能开发票吗？",  # 超边界 → 转人工
    ]
    for q in questions:
        r = agent.reply(q)
        print(f"\n客户：{q}")
        print(f"意图：{r['intent']}｜客服：{r['answer']}")
    
    print(f"\n[转人工次数]：{agent.escalated}")
    print(f"[订单查询]：{query_order('ORD-001')}")
    
    print("\n[产品清单]：")
    for p in kb.all_products():
        print(f"   {p['sku']} {p['name']} ¥{p['price']} 库存{p['stock']}")


if __name__ == "__main__":
    demo()
