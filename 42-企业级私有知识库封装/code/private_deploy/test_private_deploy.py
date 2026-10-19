#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第42篇配套 · test_private_deploy.py
验证：部署模式/数据隔离/权限/审计/离线能力/部署包

运行: python test_private_deploy.py
"""

import os
import shutil

from private_deploy import (
    DEPLOY_MODES, DataIsolation, AccountSystem, AuditLog,
    OfflineCapability, generate_package, OUTPUT_DIR,
)


def main():
    print("=" * 66)
    print("🧪 企业级私有化封装测试")
    print("=" * 66)

    # 使用独立测试目录
    shutil.rmtree("storage", ignore_errors=True)
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # 1. 部署模式
    print("\n[1] 部署模式：")
    assert len(DEPLOY_MODES) == 3
    for name, info in DEPLOY_MODES.items():
        print(f"   {name}：{info['suitable']}")

    # 2. 数据隔离
    print("\n[2] 数据隔离：")
    iso = DataIsolation("tenant_a")
    paths = iso.ensure()
    for kind, path in paths.items():
        assert os.path.isdir(path), f"目录不存在：{path}"
        print(f"   ✅ {kind}: {path}")
    # 双租户隔离
    iso_b = DataIsolation("tenant_b").ensure()
    assert iso_b["documents"] != paths["documents"]
    print(f"   ✅ 租户A/B 文档目录物理隔离")
    # 数据彻底清理
    msg = iso.purge()
    assert not os.path.exists(iso.base)
    print(f"   ✅ {msg}")

    # 3. 权限
    print("\n[3] 角色权限：")
    acc = AccountSystem(os.path.join("storage", "accounts.json"))
    acc.create_user("admin", "admin")
    acc.create_user("alice", "user")
    assert acc.can_manage("admin") and not acc.can_manage("alice")
    assert acc.can_upload("alice") and acc.can_ask("alice")
    print("   ✅ 管理员可管理，普通用户不可管理")
    print("   ✅ 普通用户可上传、可问答")

    # 4. 审计
    print("\n[4] 操作审计：")
    audit = AuditLog(os.path.join("storage", "audit", "audit.log"))
    audit.record("admin", "upload", "产品手册.pdf")
    audit.record("alice", "ask", "部署流程是什么")
    logs = audit.read_all()
    print(f"   已记录 {len(logs)} 条操作日志")
    assert len(logs) == 2 and logs[0]["action"] == "upload"
    print(f"   最近：{logs[-1]['user']} {logs[-1]['action']}")

    # 5. 离线能力
    print("\n[5] 内网/离线能力：")
    r1 = OfflineCapability.check("http://192.168.1.10:8001/v1")
    r2 = OfflineCapability.check("https://api.deepseek.com")
    print(f"   内网模型：{r1['离线可用性']}")
    print(f"   外部模型：{r2['离线可用性']}")
    assert r1["离线可用性"] == "高"

    # 6. 部署包
    print("\n[6] 生成部署包：")
    paths2 = generate_package()
    for p in paths2:
        assert os.path.exists(p) and os.path.getsize(p) > 50
        print(f"   ✅ {os.path.basename(p)}（{os.path.getsize(p)}字节）")
    assert len(paths2) == 3

    # 清理
    shutil.rmtree("storage", ignore_errors=True)
    print("\n✅ 企业级私有化封装测试通过")


if __name__ == "__main__":
    main()
