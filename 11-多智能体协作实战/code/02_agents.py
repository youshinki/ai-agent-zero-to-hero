from crewai import Agent
from config import get_llm

llm = get_llm()

researcher = Agent(
    role="研究员",
    goal="收集并整理主题相关资料，为报告提供可靠素材",
    backstory="你是一名资深研究员，擅长快速定位关键信息、筛选资料、整理要点。",
    llm=llm,
    verbose=True
)

writer = Agent(
    role="撰稿人",
    goal="根据研究员提供的资料，撰写结构清晰、内容完整的中文报告",
    backstory="你是一名优秀的内容撰稿人，擅长把资料组织成逻辑清楚、易读的正式文本。",
    llm=llm,
    verbose=True
)

reviewer = Agent(
    role="审核员",
    goal="检查报告是否完整、准确、逻辑通顺，并输出最终优化版本",
    backstory="你是一名严格的内容审核员，关注结构、事实、表达和可读性。",
    llm=llm,
    verbose=True
)
