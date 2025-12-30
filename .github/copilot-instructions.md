# Copilot instructions (RossFilter)

## Repo layout (scientific-app style)
- Installable package uses a `src/` layout (see [../pyproject.toml](../pyproject.toml)):
  - Core + UI live in [../src/rossfilter/](../src/rossfilter/)
  - Minimal tests live in [../tests/](../tests/)

## Big picture
- Entry points:
  - Installed: `python -m rossfilter` (see [../src/rossfilter/__main__.py](../src/rossfilter/__main__.py))
- UI is in [../src/rossfilter/gui.py](../src/rossfilter/gui.py) (CustomTkinter + Matplotlib). Button handlers call calculator methods and plot results.
- Orchestration is in [../src/rossfilter/calculator.py](../src/rossfilter/calculator.py): `RossFilterCalculator` holds two `Filter` instances.
- Physics/data layer is in [../src/rossfilter/filter.py](../src/rossfilter/filter.py): `Filter` is a stack of `(material, thickness)` layers and computes transmission using `xraydb.material_mu()`.
- Material discovery/validation is in [../src/rossfilter/material.py](../src/rossfilter/material.py).

## Units & data flow (don’t break)
- GUI energy inputs are **keV**; calculator converts to **eV** (see `kev_to_ev()` in [../src/rossfilter/units.py](../src/rossfilter/units.py)).
- GUI thickness inputs are **µm**; convert to **cm** via `um_to_cm()` (see [../src/rossfilter/units.py](../src/rossfilter/units.py)).
- `Filter` stores parallel lists: `materials[]` and `thicknesses[]` (cm). Preserve this structure when extending.

## Error-handling conventions
- User-facing operations prefer returning `(success: bool, payload_or_message)` over raising:
  - `Filter.add_material(...) -> (bool, str)`
  - `RossFilterCalculator.reset()/add_material_to_filter()/calculate_transmission() -> (bool, message|dict)`
- GUI prints status/errors via `RossFilterGUI.print_to_console()`.

## Packaging (Windows-first)
- Build a single-file GUI executable via PyInstaller: `python build_exe.py` (see [../build_exe.py](../build_exe.py)).
- [../build_exe.py](../build_exe.py) is intentionally Windows-only. Add a separate Linux build script in the future rather than branching behavior here.

## GUI conventions
- GUI structure uses `_setup_*` helpers plus `_calculate_transmission()`, `_reset_all()`, `_add_filter()`, `_modify_filter()` handlers (see [../src/rossfilter/gui.py](../src/rossfilter/gui.py)).
- `AutocompleteComboBox` relies on CustomTkinter internals (`self._entry`); refactor carefully.
