import PyInstaller.__main__
import xraydb
import os
from pathlib import Path


if os.name != "nt":
    raise RuntimeError(
        "build_exe.py is Windows-only. For Linux, create a separate build script later."
    )

# Get xraydb database path
xraydb_path = Path(xraydb.__file__).parent / "xraydb.sqlite"
sep = ";"

PyInstaller.__main__.run([
    'src/rossfilter/__main__.py',
    '--onefile',
    '--windowed',
    '--name=RossFilter',
    '--paths=src',
    f'--add-data={xraydb_path}{sep}xraydb',
    '--hidden-import=numpy',
    '--hidden-import=matplotlib',
    '--hidden-import=xraydb',
    '--hidden-import=sqlite3',
    '--collect-data=xraydb',
    '--collect-all=xraydb'
])

