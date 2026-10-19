#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第58篇配套 · test_tool_orchestrator.py
"""

from tool_orchestrator import (
    Tool, ToolRegistry, ToolSelector, Orchestrator, demo,
)


def main():
    print("=" * 66)
    print("🧪 工具集编排测试")
    print("=" * 66)

    print("\n[1] 注册与权限：")
    reg = ToolRegistry()
    reg.register(Tool("read_file", "读取文件", ["path"], ["path"], "user", 3))
    reg.register(Tool("delete_file", "删除文件", ["path"], ["path"], "admin", 1))
    assert len(reg.available("user")) == 1
    assert len(reg.available("admin")) == 2
    print("   ✅ 普通用户1个，管理员2个")

    print("\n[2] 参数校验：")
    t = reg.get("read_file")
    assert t.validate({"path": "a.txt"})["valid"]
    assert not t.validate({})["valid"]
    assert not t.validate({"path": "a", "x": 1})["valid"]
    print("   ✅ 必填/未知参数校验")

    print("\n[3] 选择与冲突：")
    sel = ToolSelector(reg)
    picked = sel.select("读取文件", "user")
    assert picked and picked[0].name == "read_file"
    reg.register(Tool("write_file", "写入文件", ["path", "content"],
                      ["path", "content"], "user", 2,
                      conflicts=["delete_file"]))
    reg.register(Tool("delete_file", "删除文件", ["path"], ["path"], "admin", 1,
                      conflicts=["write_file"]))
    kept = sel.resolve_conflicts([reg.get("delete_file"), reg.get("write_file")])
    assert len(kept) == 1
    print(f"   冲突消解后：{[t.name for t in kept]}")

    print("\n[4] 编排执行：")
    orch = Orchestrator()
    r = orch.execute("读取并计算", [
        {"name": "read_file", "args": {"path": "a.txt"}},
        {"name": "calculator", "args": {"expression": "1+2"}},
        {"name": "read_file", "args": {}},
    ])
    assert len(r["results"]) == 2 and len(r["errors"]) == 1
    print(f"   成功{len(r['results'])}个，错误{len(r['errors'])}个")

    print("\n[5] 权限拦截：")
    r = orch.execute("删除", [{"name": "delete_file", "args": {"path": "x"}}],
                     user_role="user")
    assert r["errors"] and "权限不足" in r["errors"][0]
    print(f"   ✅ {r['errors'][0]}")

    print("\n[6] 未知工具：")
    r = orch.execute("x", [{"name": "nope", "args": {}}])
    assert "未知工具" in r["errors"][0]
    print(f"   ✅ {r['errors'][0]}")

    print("\n[7] 演示：")
    demo()
    print("\n✅ 工具集编排测试通过")


if __name__ == "__main__":
    main()
