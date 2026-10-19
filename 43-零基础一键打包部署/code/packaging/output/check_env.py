#!/usr/bin/env python3
"""环境检测脚本：python check_env.py"""
import importlib
import os
import sys

def main():
    print("=" * 50)
    print("🔍 环境检测")
    print("=" * 50)
    ok = True
    # Python 版本
    v = sys.version_info
    status = "✅" if (v.major, v.minor) >= (3, 10) else "❌"
    print(f"{status} Python {v.major}.{v.minor}.{v.micro}（需要 3.10+）")
    ok = ok and (v.major, v.minor) >= (3, 10)
    # 依赖
    for dep in ["fastapi", "uvicorn", "pydantic", "numpy"]:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep} 已安装")
        except ImportError:
            print(f"❌ {dep} 未安装 → pip install {dep}")
            ok = False
    # .env
    if os.path.exists(".env"):
        print("✅ .env 配置文件存在")
    else:
        print("⚠️ .env 不存在，请复制 .env.example 并填写")
    print("\n" + ("✅ 环境就绪" if ok else "❌ 请先修复上述问题"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
