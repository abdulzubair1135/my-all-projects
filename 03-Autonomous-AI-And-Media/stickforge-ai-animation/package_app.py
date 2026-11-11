"""
Windows Packaging Script for StickForge AI.
Prepares distributable PyInstaller specifications and builds standalone Windows binary.
"""

from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

SPEC_CONTENT = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'PySide6',
        'playwright',
        'pydantic',
        'edge_tts',
        'pyttsx3',
        'cv2',
        'PIL',
        'numpy',
        'srt',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StickForgeAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StickForgeAI',
)
"""


def create_spec_file() -> Path:
    spec_path = PROJECT_ROOT / "stickforge.spec"
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(SPEC_CONTENT)
    print(f"[OK] Generated PyInstaller spec: {spec_path.name}")
    return spec_path


def main() -> int:
    spec_path = create_spec_file()
    print("StickForge AI packaging specification ready.")
    print("To compile full standalone distribution on Windows:")
    print("  pip install pyinstaller")
    print(f"  pyinstaller {spec_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
