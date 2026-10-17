from agent_core import BaseAgent
from rag_core import RAGCore

if __name__ == "__main__":
    # 1. 初始化RAG知识库
    rag = RAGCore()
    # 读取自定义私有文档（自行替换为你的文档路径）
    rag.init_knowledge_base("./docs/test.txt")

    # 2. 初始化智能体
    agent = BaseAgent()
    print("\n=== 私有文档问答Agent 已启动 ===")

    while True:
        user_input = input
