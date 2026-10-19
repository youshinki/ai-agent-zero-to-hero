#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第41篇配套 · test_commercial_v2.py
验证：双环境隔离/调试扫描/友好容错/配置模板/清单

运行: python test_commercial_v2.py
"""

import os
import shutil

from commercial_v2 import (
    Environment, DebugScanner, FriendlyErrors, DEBUG_CLEANUP,
    build_env_template, build_checklist, OUTPUT_DIR,
)


def main():
    print("=" * 66)
    print("🧪 高阶商业化改造测试")
    print("=" * 66)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # 1. 双环境
    print("\n[1] 双环境隔离：")
    dev = Environment("development")
    prod = Environment("production")
    print(f"   开发：debug={dev.config['debug_logs']}, traceback={dev.config['show_traceback']}")
    print(f"   生产：debug={prod.config['debug_logs']}, traceback={prod.config['show_traceback']}")
    assert dev.config["debug_logs"] and not prod.config["debug_logs"]
    assert prod.config["pretty_errors"]

    # 2. 生产模式静默日志
    print("\n[2] 生产模式日志过滤：")
    print("   （生产模式 debug 日志应被过滤）")
    prod.log("debug", "这条调试不该出现")
    prod.log("info", "这条必要状态应出现")

    # 3. 调试痕迹扫描
    print("\n[3] 调试痕迹扫描：")
    os.makedirs("scan_demo", exist_ok=True)
    with open("scan_demo/bad_code.py", "w", encoding="utf-8") as f:
        f.write('''API_KEY = "sk-test123456789"
print("debug info")
# TODO: 临时逻辑
path = "/Users/test/data"
''')
    findings = DebugScanner.scan_dir("scan_demo")
    assert findings, "应检测到调试痕迹"
    for path, items in findings.items():
        for item in items:
            print(f"   ⚠️ {item['type']}（第{item['line']}行）")
    types = {i["type"] for items in findings.values() for i in items}
    assert "print调试" in types and "硬编码密钥" in types

    # 4. 友好容错
    print("\n[4] 友好容错：")
    cases = [FileNotFoundError("x"), ConnectionError("x"), TimeoutError("x"),
             KeyError("x"), PermissionError("x"), RuntimeError("x")]
    for e in cases:
        print(f"   {type(e).__name__} → {FriendlyErrors.friendly(e)}")
    assert "文件" in FriendlyErrors.friendly(FileNotFoundError())

    # 5. 清单与模板
    print("\n[5] 生成清单与配置模板：")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    env = build_env_template()
    checklist = build_checklist()
    assert "APP_ENV" in env and "API_KEY" in env
    assert "调试痕迹清理" in checklist and "双环境开关" in checklist
    with open(os.path.join(OUTPUT_DIR, ".env.example"), "w", encoding="utf-8") as f:
        f.write(env)
    with open(os.path.join(OUTPUT_DIR, "商业化改造清单.md"), "w", encoding="utf-8") as f:
        f.write(checklist)
    print(f"   ✅ .env.example")
    print(f"   ✅ 商业化改造清单.md")

    # 6. 清理扫描演示目录
    shutil.rmtree("scan_demo", ignore_errors=True)
    print("\n✅ 高阶商业化改造测试通过")


if __name__ == "__main__":
    main()
