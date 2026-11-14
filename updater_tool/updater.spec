# -*- mode: python ; coding: utf-8 -*-
"""独立更新器的 PyInstaller 打包配置.

打包命令 (在 updater_tool/ 目录下):
    pyinstaller updater.spec --noconfirm
产出:
    dist/SanktecoUpdater
"""
a = Analysis(
    ["updater_main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    # 显式排除主程序依赖, 保持更新器体积小
    excludes=["PySide2", "qframelesswindow", "tufup", "loguru", "requests"],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SanktecoUpdater",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)