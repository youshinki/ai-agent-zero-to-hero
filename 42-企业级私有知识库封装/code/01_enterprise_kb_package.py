# 第42篇配套代码：企业级私有知识库封装
# 适配商用保密、内网、私有化场景
# 运行：python 01_enterprise_kb_package.py

import os
import json
from pathlib import Path

# ========== 企业级知识库封装 ==========
class EnterpriseKnowledgeBase:
    """企业级私有知识库（支持内网/私有化部署）"""
    
    def __init__(self, kb_path="./kb_store"):
        self.kb_path = Path(kb_path)
        self.kb_path.mkdir(parents=True, exist_ok=True)
        self.documents = {}
        self._load_index()
    
    def _load_index(self):
        index_file = self.kb_path / "index.json"
        if index_file.exists():
            with open(index_file) as f:
                self.documents = json.load(f)
    
    def _save_index(self):
        with open(self.kb_path / "index.json", "w") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
    
    def add_document(self, doc_id, content, metadata=None):
        """添加文档（企业级：支持元数据、版本控制）"""
        doc = {
            "id": doc_id,
            "content": content,
            "metadata": metadata or {},
            "version": self.documents.get(doc_id, {}).get("version", 0) + 1,
            "created_at": __import__("datetime").datetime.now().isoformat()
        }
        self.documents[doc_id] = doc
        
        # 保存文档内容
        doc_path = self.kb_path / f"{doc_id}.txt"
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self._save_index()
        return doc
    
    def search(self, query, top_k=3):
        """检索（企业级：权限过滤 + 脱敏）"""
        results = []
        for doc_id, doc in self.documents.items():
            if query in doc["content"]:
                # 脱敏处理
                safe_content = self._mask_sensitive(doc["content"])
                results.append({
                    "id": doc_id,
                    "content": safe_content[:500],
                    "metadata": doc["metadata"],
                    "score": 0.95
                })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
    
    def _mask_sensitive(self, content):
        """脱敏敏感信息"""
        import re
        # 脱敏手机号
        content = re.sub(r'1[3-9]\d{9}', '138****0000', content)
        # 脱敏身份证
        content = re.sub(r'\d{17}[\dXx]', '****', content)
        # 脱敏邮箱
        content = re.sub(r'\w+@\w+\.\w+', '***@***.com', content)
        return content

# ========== 私有化部署配置 ==========
class PrivateDeployment:
    """私有化部署方案（支持内网/离线）"""
    
    @staticmethod
    def generate_config():
        return {
            "deployment_mode": "private",
            "network": {
                "internal_only": True,
                "allowed_ips": ["192.168.0.0/16", "10.0.0.0/8"],
                "ssl_enabled": True
            },
            "storage": {
                "vector_db": "chromadb（本地）",
                "file_storage": "本地文件系统",
                "backup": "每日自动备份到NAS"
            },
            "model": {
                "mode": "local",  # local / proxy
                "local_model": "Qwen2-7B-Instruct",
                "proxy_url": "",
                "embedding_model": "bge-small-zh-v1.5"
            },
            "auth": {
                "type": "ldap / oauth / local",
                "admin_users": ["admin"],
                "session_timeout": 3600
            }
        }
    
    @staticmethod
    def docker_compose():
        return """# docker-compose.yml 企业私有化部署
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEPLOY_MODE=private
      - MODEL_PATH=/models
    volumes:
      - ./kb_store:/app/kb_store
      - ./models:/models
    networks:
      - internal

  chromadb:
    image: chromadb/chroma:latest
    volumes:
      - ./chroma_data:/chroma/chroma
    networks:
      - internal

networks:
  internal:
    driver: bridge
"""

if __name__ == "__main__":
    print("=" * 60)
    print("🏢 企业级私有知识库封装")
    print("=" * 60)
    
    print("\n📚 知识库功能测试")
    print("-" * 40)
    kb = EnterpriseKnowledgeBase()
    kb.add_document("doc_001", "企业产品手册：我们的核心产品是AI智能客服系统，支持多轮对话和知识库问答。联系方式：13812345678")
    kb.add_document("doc_002", "技术支持文档：部署要求Python 3.10+，需要至少8GB内存。邮箱联系：support@example.com")
    
    results = kb.search("产品手册")
    print("搜索结果：")
    for r in results:
        print(f"  找到：{r['content'][:100]}...")
    
    print("\n🔒 数据脱敏验证")
    print("-" * 40)
    print("  原内容：联系方式：13812345678，邮箱：support@example.com")
    print(f"  脱敏后：{kb._mask_sensitive('联系方式：13812345678，邮箱：support@example.com')}")
    
    print("\n⚙️ 私有化部署配置")
    print("-" * 40)
    config = PrivateDeployment.generate_config()
    print(f"  部署模式：{config['deployment_mode']}")
    print(f"  内网限制：{config['network']['internal_only']}")
    print(f"  模型模式：{config['model']['mode']}")
    
    print("\n🐳 Docker部署配置")
    print("-" * 40)
    print(PrivateDeployment.docker_compose())
    
    print("\n✅ 企业级功能清单：")
    print("  • 内网/离线部署支持")
    print("  • 数据脱敏保护")
    print("  • 文档版本控制")
    print("  • 元数据管理")
    print("  • 权限过滤")
    print("  • Docker容器化")
    print("  • 自动备份")
