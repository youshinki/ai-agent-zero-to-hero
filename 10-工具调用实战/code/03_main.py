from agent_core import OfficeAgent
from rag_core import RAGCore

if __name__ == "__main__":
    # 初始化RAG知识库（可选，有文档就加载）
    use_rag = input("是否加载知识库？(y/n)：").strip().lower()
    rag = None
    if use_rag == "y":
        rag = RAGCore()
        rag.init_knowledge_base("./docs/test.txt")

    # 初始化Agent
    agent = OfficeAgent()
    print("\n=== 自动化办公Agent 已启动 ===")
    print("支持功能：时间查询、文件读取、数学计算、知识库问答")

    while True:
        user_input = input("\n请输入任务：")
        if user_input in ["exit", "quit", "退出"]:
            print("Agent已退出")
            break

        # 如果开启了RAG，先检索知识库
        knowledge = ""
        if rag:
            knowledge = rag.search_relevant(user_input)
            agent.set_knowledge(knowledge)

        # 运行Agent完整闭环
        result = agent.run(user_input)
        print("\n【最终答案】")
        print(result)
