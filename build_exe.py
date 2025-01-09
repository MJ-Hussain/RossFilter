import PyInstaller.__main__
import xraydb
import os
from pathlib import Path

# Get xraydb database path
xraydb_path = Path(xraydb.__file__).parent / "xraydb.sqlite"

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=RossFilter',
    f'--add-data={xraydb_path};xraydb',  # Use semicolon for Windows, colon for Unix
    '--hidden-import=numpy',
    '--hidden-import=matplotlib',
    '--hidden-import=xraydb',
    '--hidden-import=sqlite3',
    '--collect-data=xraydb',
    '--collect-all=xraydb'
])
