#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第43篇配套 · test_packaging.py
验证：bat 脚本/环境检测/PyInstaller配置/启动入口/README

运行: python test_packaging.py
"""

import os
import shutil

from packaging import generate_package, OUTPUT_DIR


def main():
    print("=" * 66)
    print("🧪 一键打包部署测试")
    print("=" * 66)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    print("\n[1] 生成部署包：")
    paths = generate_package("AI_Agent_App")
    for p in paths:
        assert os.path.exists(p) and os.path.getsize(p) > 50
        print(f"   ✅ {os.path.basename(p)}（{os.path.getsize(p)}字节）")
    assert len(paths) == 8

    # 2. 关键脚本内容校验
    print("\n[2] 脚本内容校验：")
    checks = {
        "install.bat": ["检测 Python", "创建虚拟环境", "安装依赖", "初始化配置"],
        "start.bat": ["启动", "venv", "main.py"],
        "uninstall.bat": ["卸载", "删除虚拟环境"],
        "check_env.py": ["环境检测", "Python", "fastapi"],
        "AI_Agent_App.spec": ["Analysis", "EXE", "hiddenimports"],
        "main.py": ["FastAPI", "/health", "/api/chat", "uvicorn.run"],
        "README.md": ["一键打包部署说明", "install.bat", "start.bat"],
    }
    for fname, keywords in checks.items():
        path = os.path.join(OUTPUT_DIR, fname)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        for kw in keywords:
            assert kw in content, f"{fname} 缺少：{kw}"
        print(f"   ✅ {fname}：{', '.join(keywords)}")

    # 3. 语法检查（check_env.py / main.py）
    print("\n[3] Python语法检查：")
    import ast
    for fname in ["check_env.py", "main.py"]:
        path = os.path.join(OUTPUT_DIR, fname)
        with open(path, encoding="utf-8") as f:
            ast.parse(f.read())
        print(f"   ✅ {fname} 语法正确")

    # 4. 打包产物说明
    print("\n[4] 打包说明：")
    print("   - Windows：双击 install.bat → 编辑.env → start.bat")
    print("   - Linux/macOS：bash start.sh")
    print("   - exe：pyinstaller AI_Agent_App.spec")

    print("\n✅ 一键打包部署测试通过")


if __name__ == "__main__":
    main()
