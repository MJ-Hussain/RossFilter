# RossFilter

Small scientific GUI app to compute X-ray transmission through up to two “Ross filter” stacks.

## Run

Best practice for development (editable install):

```bash
python -m pip install -e .
rossfilter
```

## Build Windows executable (PyInstaller)

```bash
python -m pip install -e .[dev]
python build_exe.py
```

Notes:
- `build_exe.py` is Windows-only and will error on non-Windows.
