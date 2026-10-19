# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置：pyinstaller AI_Agent_App.spec
# 生成单文件 exe：dist/AI_Agent_App.exe

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('knowledge_base', 'knowledge_base'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'uvicorn', 'fastapi', 'pydantic', 'numpy',
        'apscheduler', 'json', 'sqlite3',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AI_Agent_App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)
