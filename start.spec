# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/start.py'], # 注意这里是入口路径
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('locales', 'locales'),
        ('docs', 'docs'),
    ],
    hiddenimports=['tufup', 'bsdiff4', 'requests'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='Sankteco',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False,
    name='Sankteco'
)