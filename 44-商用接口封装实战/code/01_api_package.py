# 第44篇配套代码：商用接口封装实战
# AI系统对外标准化调用，适配二次开发
# 运行：python 01_api_package.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import json

# ========== 标准请求/响应模型 ==========
class ChatRequest(BaseModel):
    """标准聊天请求"""
    message: str
    session_id: Optional[str] = ""
    user_id: Optional[str] = ""
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    """标准聊天响应"""
    success: bool
    data: Optional[str] = None
    error: Optional[str] = None
    session_id: str = ""
    usage: dict = {}

class KBSearchRequest(BaseModel):
    """知识库搜索请求"""
    query: str
    top_k: Optional[int] = 3
    user_id: Optional[str] = ""

class KBSearchResponse(BaseModel):
    """知识库搜索响应"""
    success: bool
    results: List[dict] = []
    total: int = 0

# ========== API验证 ==========
class AuthMiddleware:
    """API认证中间件"""
    
    def __init__(self, api_keys=None):
        self.api_keys = api_keys or ["sk-default-key"]
    
    def verify(self, api_key: str):
        if api_key not in self.api_keys:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return api_key

# ========== 接口封装 ==========
class CommercialAPI:
    """商用API封装"""
    
    @staticmethod
    def wrap_response(success=True, data=None, error=None, **kwargs):
        """统一响应格式"""
        resp = {"success": success, "data": data, "error": error}
        resp.update(kwargs)
        return resp
    
    @staticmethod
    def error_response(code: int, message: str):
        """标准错误响应"""
        return {
            "success": False,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    @staticmethod
    def paginate(items, page=1, page_size=20):
        """分页封装"""
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "items": items[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

# ========== 版本控制 ==========
class APIVersion:
    """API版本管理"""
    
    VERSIONS = {
        "v1": {"status": "deprecated", "sunset": "2024-12-31"},
        "v2": {"status": "stable", "features": ["chat", "kb_search", "batch"]},
        "v3": {"status": "beta", "features": ["stream", "multi_modal"]}
    }
    
    @staticmethod
    def get_version_info(version):
        return APIVersion.VERSIONS.get(version, {"status": "unknown"})

# ========== SDK示例 ==========
class PythonSDK:
    """Python SDK示例"""
    
    def __init__(self, api_key, base_url="http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        import requests
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def chat(self, message, session_id=""):
        """聊天接口"""
        resp = self.session.post(
            f"{self.base_url}/api/v2/chat",
            json={"message": message, "session_id": session_id}
        )
        return resp.json()
    
    def search_kb(self, query, top_k=3):
        """知识库搜索"""
        resp = self.session.post(
            f"{self.base_url}/api/v2/kb/search",
            json={"query": query, "top_k": top_k}
        )
        return resp.json()

if __name__ == "__main__":
    print("=" * 60)
    print("🔌 商用接口封装实战")
    print("=" * 60)
    
    print("\n1️⃣ 标准API接口列表")
    print("-" * 40)
    print("""
POST /api/v2/chat          # 聊天接口
POST /api/v2/kb/search     # 知识库搜索
POST /api/v2/kb/add        # 添加文档
GET  /api/v2/health        # 健康检查
GET  /api/v2/usage         # 用量统计
""")
    
    print("\n2️⃣ 统一请求/响应格式")
    print("-" * 40)
    req = ChatRequest(message="你好", session_id="sess_001")
    print(f"请求：{req.model_dump()}")
    resp = CommercialAPI.wrap_response(data="你好！有什么可以帮助你的？", session_id="sess_001")
    print(f"响应：{json.dumps(resp, ensure_ascii=False, indent=2)}")
    
    print("\n3️⃣ 错误码规范")
    errors = [
        (1001, "认证失败"),
        (1002, "频率限制"),
        (2001, "参数错误"),
        (3001, "处理异常"),
        (4001, "上游服务错误")
    ]
    for code, msg in errors:
        print(f"  {code}: {msg}")
    
    print("\n4️⃣ 分页封装")
    items = [{"id": i, "name": f"doc_{i}"} for i in range(25)]
    page = CommercialAPI.paginate(items, page=2, page_size=10)
    print(f"  第{page['page']}页，共{page['total']}条，{page['total_pages']}页")
    
    print("\n5️⃣ API版本管理")
    for ver, info in APIVersion.VERSIONS.items():
        print(f"  {ver}: {info['status']} - {info}")
    
    print("\n6️⃣ SDK使用示例")
    print("-" * 40)
    print("""
# 安装SDK
pip install my-ai-agent-sdk

# 使用
from my_agent import AgentSDK

client = AgentSDK(api_key="sk-xxx")
response = client.chat("你好")
print(response.data)
""")
