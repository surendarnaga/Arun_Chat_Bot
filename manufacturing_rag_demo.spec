# PyInstaller spec for Windows packaging
from pathlib import Path

project_dir = Path(__file__).resolve().parent

added_files = [
    (str(project_dir / "static"), "static"),
    (str(project_dir / "data" / "docs"), "sample_docs"),
]

block_cipher = None


a = Analysis(
    [str(project_dir / "run_demo.py")],
    pathex=[str(project_dir)],
    binaries=[],
    datas=added_files,
    hiddenimports=["sklearn.utils._typedefs", "sklearn.utils._cython_blas", "sklearn.neighbors._partition_nodes"],
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
    name="ManufacturingRAGDemo",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ManufacturingRAGDemo",
)
