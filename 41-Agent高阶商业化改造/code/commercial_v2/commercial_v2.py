#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第41篇配套完整项目代码 · commercial_v2.py
Agent 高阶商业化改造：
  1. 双环境隔离（开发 / 生产）
  2. 调试痕迹全局清理
  3. 废弃代码/冗余文件扫描
  4. 友好交互与容错
  5. 敏感配置抽离

运行: python commercial_v2.py    # 生成改造清单与配置模板到 output/
"""

import os
import re

OUTPUT_DIR = "output"


# ======================================================================
# 一、双环境隔离
# ======================================================================

class Environment:
    """一套代码，两种运行环境"""
    
    MODES = {
        "development": {
            "debug_logs": True,
            "show_traceback": True,
            "cache_enabled": False,
            "pretty_errors": False,
            "log_level": "DEBUG",
        },
        "production": {
            "debug_logs": False,
            "show_traceback": False,
            "cache_enabled": True,
            "pretty_errors": True,
            "log_level": "WARNING",
        },
    }
    
    def __init__(self, mode: str = "production"):
        if mode not in self.MODES:
            raise ValueError("mode 必须是 development 或 production")
        self.mode = mode
        self.config = self.MODES[mode]
    
    @property
    def is_prod(self) -> bool:
        return self.mode == "production"
    
    def log(self, level: str, message: str):
        """生产模式只输出必要状态；开发模式全部输出"""
        if self.is_prod and level == "debug":
            return
        print(f"[{level.upper()}] {message}")


# ======================================================================
# 二、调试痕迹清理清单
# ======================================================================

DEBUG_CLEANUP = {
    "日志清理": [
        "删除切片详情、检索分数、模型原始参数打印",
        "删除请求报文、响应源码打印",
        "保留：启动成功、初始化完成、入库成功等必要提示",
        "关闭框架 DEBUG 模式",
    ],
    "废弃代码": [
        "注释掉的旧代码、废弃函数",
        "临时测试逻辑、写死的本地路径",
        "测试密钥、固定参数",
        "多余调试接口、测试按钮、备用入口",
        "独立测试脚本、临时启动文件",
    ],
    "冗余文件": [
        "向量库临时缓存、日志缓存、运行缓存",
        "测试 PDF、测试文档、样本素材",
        "编译缓存（__pycache__）、临时配置",
        "自动生成的垃圾文件",
    ],
}

KEEP_FILES = ["核心源码", "配置文件（模板）", "启动脚本", "使用文档"]


# ======================================================================
# 三、代码扫描器（检测调试痕迹）
# ======================================================================

class DebugScanner:
    """扫描代码中的调试痕迹与敏感信息"""
    
    PATTERNS = {
        "print调试": r"\bprint\s*\(",
        "硬编码密钥": r"(sk-[A-Za-z0-9]{10,}|API_KEY\s*=\s*['\"][^'\"]+['\"])",
        "TODO/FIXME": r"(TODO|FIXME|XXX|HACK)",
        "本地绝对路径": r"(/Users/|C:\\\\Users\\\\|/home/)",
        "调试断点": r"(breakpoint\(\)|pdb\.set_trace)",
        "敏感端口": r"(localhost:\d+|127\.0\.0\.1:\d+)",
    }
    
    @classmethod
    def scan_file(cls, path: str) -> list:
        findings = []
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except OSError:
            return findings
        for name, pattern in cls.PATTERNS.items():
            for m in re.finditer(pattern, content):
                line = content[:m.start()].count("\n") + 1
                findings.append({"type": name, "line": line,
                                 "code": content.splitlines()[line-1][:60].strip()})
        return findings
    
    @classmethod
    def scan_dir(cls, root: str) -> dict:
        result = {}
        for dirpath, _, files in os.walk(root):
            if "__pycache__" in dirpath:
                continue
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                findings = cls.scan_file(path)
                if findings:
                    result[path] = findings
        return result


# ======================================================================
# 四、友好容错与交互
# ======================================================================

class FriendlyErrors:
    """把底层报错转成普通人能看懂的提示"""
    
    MESSAGES = {
        "FileNotFoundError": "找不到所需文件，请检查资料是否已正确放置。",
        "ConnectionError": "网络连接异常，请检查网络后重试。",
        "TimeoutError": "请求超时，请稍后重试。",
        "KeyError": "配置项缺失，请联系管理员完成配置。",
        "PermissionError": "权限不足，请联系管理员。",
        "Exception": "系统繁忙，请稍后重试。",
    }
    
    @classmethod
    def friendly(cls, exc: Exception) -> str:
        name = type(exc).__name__
        for key, msg in cls.MESSAGES.items():
            if key != "Exception" and key in name:
                return msg
        return cls.MESSAGES["Exception"]
    
    @staticmethod
    def loading_states() -> dict:
        return {
            "loading": "正在加载资料，请稍候...",
            "thinking": "正在思考并检索知识库...",
            "success": "回答完成",
            "empty": "暂未查询到相关内容，请换个问法或补充资料。",
            "error": "系统繁忙，请稍后重试。",
        }


# ======================================================================
# 五、生成改造材料
# ======================================================================

def build_env_template() -> str:
    return """# ===== 环境变量模板（交付时由客户自行填写）=====

# 运行环境：development / production
APP_ENV=production

# 大模型配置
API_KEY=your-api-key-here
BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat

# 服务配置
HOST=0.0.0.0
PORT=8000

# 检索与压缩参数
TOP_K=3
MAX_CONTEXT_TOKEN=1800
COMPRESS_THRESHOLD=20

# 日志级别（生产建议 WARNING）
LOG_LEVEL=WARNING
"""


def build_checklist() -> str:
    out = ["# 高阶商业化改造清单\n"]
    out.append("## 一、调试痕迹清理")
    for cat, items in DEBUG_CLEANUP.items():
        out.append(f"### {cat}")
        for i in items:
            out.append(f"- [ ] {i}")
        out.append("")
    out.append("## 二、最终目录只保留")
    for f in KEEP_FILES:
        out.append(f"- [x] {f}")
    out.append("\n## 三、双环境开关")
    out.append("- APP_ENV=development：详细日志、暴露报错、便于调试")
    out.append("- APP_ENV=production：静默日志、友好提示、开启容错")
    out.append("\n## 四、友好提示")
    for k, v in FriendlyErrors.loading_states().items():
        out.append(f"- {k}：{v}")
    return "\n".join(out)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, ".env.example"), "w", encoding="utf-8") as f:
        f.write(build_env_template())
    with open(os.path.join(OUTPUT_DIR, "商业化改造清单.md"), "w", encoding="utf-8") as f:
        f.write(build_checklist())
    print("=" * 60)
    print("🏭 高阶商业化改造材料已生成")
    print("=" * 60)
    print(f"   ✅ {OUTPUT_DIR}/.env.example")
    print(f"   ✅ {OUTPUT_DIR}/商业化改造清单.md")
