# -*- coding: utf-8 -*-
# 分工模式（Pipeline）：选题->脚本->配图->审核，流水线串联
def agent_topic(topic):
    return ""  # 占位：选题 Agent 产出大纲

def agent_script(outline):
    return ""  # 占位：脚本 Agent 消费大纲

def agent_image(script_snippet):
    return ""  # 占位：配图 Agent 产出配图提示词

def agent_review(script):
    return ""  # 占位：审核 Agent 返回审核意见


def pipeline_chain(topic):
    outline = agent_topic(topic)          # 1. 选题 Agent
    script = agent_script(outline)        # 2. 脚本 Agent，消费大纲
    images = agent_image(script[:500])    # 3. 配图 Agent，消费脚本关键点
    review = agent_review(script)         # 4. 审核 Agent 把关
    return {"script": script, "images": images, "review": review}
