# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Cece v1.3
# Enhanced chess engine with dynamic evaluation and tactical improvements

a = Analysis(
    ['cece_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['chess', 'chess.engine', 'chess.pgn', 'chess.svg', 'chess.polyglot'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Cece_v1.3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
