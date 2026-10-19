#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第42篇配套完整项目代码 · private_deploy.py
企业级私有知识库封装：
  1. 私有化部署模式（本地/内网/自有云）
  2. 数据隔离（文档/运行/账号/审计）
  3. 内网运行与离线能力
  4. 角色权限（管理员/普通用户）
  5. 操作审计日志

运行: python private_deploy.py    # 生成部署包到 output/
"""

import json
import os
from datetime import datetime

OUTPUT_DIR = "output"


# ======================================================================
# 一、部署模式
# ======================================================================

DEPLOY_MODES = {
    "本地单机版": {
        "suitable": "小微企业、律所、教育机构、工作室",
        "features": ["客户一台电脑/服务器即可安装", "内网IP访问", "数据留在本地",
                     "不强制上传外部文档"],
        "requirements": ["2核CPU / 8GB内存 / 50GB磁盘"],
    },
    "内网主机版": {
        "suitable": "有内网服务器的企业",
        "features": ["内网域名/IP访问", "不开放高危端口", "支持自定义端口",
                     "离线/弱网环境可运行基础功能"],
        "requirements": ["4核CPU / 16GB内存 / 100GB磁盘", "内网固定IP"],
    },
    "企业标准版": {
        "suitable": "中大型企业、多部门",
        "features": ["多用户权限", "操作审计", "日志留存", "私有模型接入",
                     "数据备份与恢复"],
        "requirements": ["8核CPU / 32GB内存 / 500GB磁盘", "可选GPU"],
    },
}


# ======================================================================
# 二、数据隔离
# ======================================================================

class DataIsolation:
    """四类数据隔离：文档/运行/账号/审计"""
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.base = os.path.join("storage", tenant_id)
        self.paths = {
            "documents": os.path.join(self.base, "documents"),
            "runtime": os.path.join(self.base, "runtime"),
            "accounts": os.path.join(self.base, "accounts"),
            "audit": os.path.join(self.base, "audit"),
        }
    
    def ensure(self) -> dict:
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)
        return self.paths
    
    def path_of(self, kind: str) -> str:
        return self.paths[kind]
    
    def purge(self) -> str:
        """删除客户数据后彻底清理"""
        import shutil
        shutil.rmtree(self.base, ignore_errors=True)
        return f"已彻底清理租户数据：{self.base}"


# ======================================================================
# 三、权限与审计
# ======================================================================

class AccountSystem:
    def __init__(self, store_path: str = None):
        self.store_path = store_path or os.path.join("storage", "accounts.json")
        self.users = {}
        self._load()
    
    def _load(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.users = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.users = {}
    
    def _save(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def create_user(self, username: str, role: str = "user") -> dict:
        if role not in ("admin", "user"):
            raise ValueError("角色必须是 admin 或 user")
        self.users[username] = {"role": role, "created": datetime.now().isoformat()}
        self._save()
        return self.users[username]
    
    def can_upload(self, username: str) -> bool:
        """文档上传权限：管理员与普通用户均可（普通用户受配额限制）"""
        return username in self.users
    
    def can_manage(self, username: str) -> bool:
        """系统管理权限：仅管理员"""
        return self.users.get(username, {}).get("role") == "admin"
    
    def can_ask(self, username: str) -> bool:
        return username in self.users


class AuditLog:
    def __init__(self, path: str = None):
        self.path = path or os.path.join("storage", "audit", "audit.log")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
    
    def record(self, user: str, action: str, detail: str = "") -> dict:
        entry = {
            "time": datetime.now().isoformat(),
            "user": user, "action": action, "detail": detail,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry
    
    def read_all(self) -> list:
        if not os.path.exists(self.path):
            return []
        out = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return out


# ======================================================================
# 四、内网与离线能力
# ======================================================================

class OfflineCapability:
    """内网/离线运行检查"""
    
    CHECK_ITEMS = {
        "模型地址可配置": "支持改为客户本地私有模型地址（如 http://192.168.1.10:8001/v1）",
        "不依赖外网": "核心问答/检索不调用外网；模型若用本地部署则完全离线",
        "端口可配置": "PORT 环境变量可改，避免占用高危端口",
        "内网IP访问": "HOST=0.0.0.0，内网通过服务器IP访问",
        "离线兜底": "无外网时返回友好提示，不崩溃",
    }
    
    @classmethod
    def check(cls, base_url: str = "") -> dict:
        results = {}
        is_local = any(k in base_url for k in ["192.168.", "127.0.0.1", "localhost"])
        results["模型地址"] = "本地/内网模型" if is_local else "外部模型（需外网）"
        results["离线可用性"] = "高" if is_local else "依赖外网"
        return results


# ======================================================================
# 五、生成部署包
# ======================================================================

def docker_compose() -> str:
    return """version: '3.8'

services:
  app:
    build: .
    ports:
      - "${PORT:-8000}:8000"
    environment:
      - APP_ENV=production
      - API_KEY=${API_KEY}
      - BASE_URL=${BASE_URL}
      - MODEL_NAME=${MODEL_NAME}
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
    restart: unless-stopped

  # 可选：本地嵌入/重排服务
  # embedding:
  #   image: your-local-embedding:latest
  #   ports: ["8001:8001"]
"""


def env_private() -> str:
    return """# ===== 企业私有化部署配置 =====
APP_ENV=production
HOST=0.0.0.0
PORT=8000

# 私有模型地址（内网）
API_KEY=your-private-key
BASE_URL=http://192.168.1.10:8001/v1
MODEL_NAME=local-model

# 数据目录（本地存储，不出内网）
DATA_DIR=./storage
LOG_DIR=./logs

# 权限
ADMIN_USER=admin
ADMIN_PASSWORD=change-me-on-first-login
"""


def generate_package():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = {
        "docker-compose.yml": docker_compose(),
        ".env.private": env_private(),
        "部署说明.md": "# 企业私有化部署说明\n\n" + "\n".join(
            f"## {name}\n- 适合：{info['suitable']}\n"
            + "\n".join(f"- {x}" for x in info["features"])
            + "\n- 环境：" + "；".join(info["requirements"]) + "\n"
            for name, info in DEPLOY_MODES.items()
        ) + "\n## 内网离线能力\n" + "\n".join(
            f"- {k}：{v}" for k, v in OfflineCapability.CHECK_ITEMS.items()
        ),
    }
    paths = []
    for name, content in files.items():
        path = os.path.join(OUTPUT_DIR, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        paths.append(path)
    return paths


if __name__ == "__main__":
    print("=" * 60)
    print("🏢 生成企业私有化部署包")
    print("=" * 60)
    for p in generate_package():
        print(f"   ✅ {p}")
