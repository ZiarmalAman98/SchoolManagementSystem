# PyInstaller one-folder build for Windows.
from pathlib import Path

block_cipher = None
project = Path(SPECPATH)

a = Analysis(
    [str(project / "run.py")],
    pathex=[str(project)],
    binaries=[],
    datas=[],
    hiddenimports=["sqlalchemy.dialects.sqlite", "PySide6.QtPrintSupport"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SchoolManagementSystem",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True, name="SchoolManagementSystem")