from commercial.commercial_wrapper import commercial_agent
from commercial.batch_upload import batch_uploader
from commercial.safe_privacy import privacy_safe

class EnterpriseRAGSystem:
    def __init__(self):
        print("✅ 企业私有知识库系统｜商用模式启动成功")

    def init_company_docs(self):
        """初始化企业全部资料"""
        return batch_uploader.batch_import_all()

    def chat(self, user_input: str) -> str:
        """企业商用问答入口（最终对外接口）"""
        # 1. 隐私安全拦截
        safe_check = privacy_safe.forbid_external_leak(user_input)
        if not safe_check:
            return "抱歉，无法提供相关查询内容，仅支持业务资料问答。"

        # 2. 商业化智能问答
        raw_answer = commercial_agent.safe_answer(user_input)

        # 3. 最终安全过滤输出
        final_answer = privacy_safe.safe_reply_filter(user_input, raw_answer)

        return final_answer

# 企业商用全局实例
enterprise_rag = EnterpriseRAGSystem()

# 快速测试
if __name__ == "__main__":
    # 首次部署先导入全部企业资料
    # print(enterprise_rag.init_company_docs())

    while True:
        q = input("企业提问：")
        if q in ["exit", "退出"]:
            break
        print(enterprise_rag.chat(q))
