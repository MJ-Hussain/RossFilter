# Copilot instructions (RossFilter)

## Repo layout (scientific-app style)
- Installable package uses a `src/` layout (see [../pyproject.toml](../pyproject.toml)):
  - App code: [../src/rossfilter/](../src/rossfilter/)
  - Tests: [../tests/](../tests/)

## Dev workflows (the non-obvious bits)
- Run GUI (dev): `python -m pip install -e .` then `rossfilter` (see [../README.md](../README.md)).
- Run module entrypoint: `python -m rossfilter` (see [../src/rossfilter/__main__.py](../src/rossfilter/__main__.py)).
- Tests: `pytest` (tests hit `xraydb`, and assume common materials like `Be`/`Al` exist).

## Architecture & data flow (read this first)
- UI layer: [../src/rossfilter/gui.py](../src/rossfilter/gui.py) (CustomTkinter) collects inputs, calls calculator methods, and plots via `PlotManager`.
- Orchestration: [../src/rossfilter/calculator.py](../src/rossfilter/calculator.py)
  - `RossFilterCalculator.channels: list[Channel]` is the app state.
  - `calculate_transmission()` computes per-channel transmissions plus sequential differences (Ch1–Ch2, Ch2–Ch3, ...).
- Physics/data: [../src/rossfilter/filter.py](../src/rossfilter/filter.py)
  - `Channel.filters: list[Filter]` where `Filter` is a dataclass with `material`, `thickness` (cm), optional `density`.
  - Transmission uses `xraydb.material_mu(material, energy_ev, density=...)` then Beer–Lambert: `exp(-mu * thickness_cm)`.
- Plotting: [../src/rossfilter/plot_manager.py](../src/rossfilter/plot_manager.py) wraps a Matplotlib Figure embedded in Tk.

## Units (don’t break)
- GUI energy fields are **keV**; core computations use **eV** via `kev_to_ev()` in [../src/rossfilter/units.py](../src/rossfilter/units.py).
- GUI thickness is **µm**; `RossFilterCalculator.add_filter_to_channel()` converts to **cm** via `um_to_cm()`.
- Filter thickness stored in `Filter.thickness` is **cm**.

## Error-handling conventions (match existing style)
- Backend methods used by the GUI return `(success: bool, message_or_result)` instead of raising (e.g. `add_filter_to_channel()`, `remove_channel()`, `calculate_transmission()`).
- `Channel.add_filter()/update_filter()` validate via `validate_material()` in [../src/rossfilter/material.py](../src/rossfilter/material.py) and return `(bool, str)`.

## GUI conventions (avoid breaking fragile parts)
- UI is built via `_setup_*` helpers; action handlers are `_add_channel()`, `_add_filter()`, `_edit_filter()`, `_delete_*()`, `_calculate()`, `_reset()`.
- Selection/checkboxes are keyed tuples like `("channel", c_idx)` and `("filter", c_idx, f_idx)`; plotting uses these keys in `_plot_selected_series()`.
- `AutocompleteComboBox` relies on CustomTkinter internals (`self._entry`, `_open_dropdown_menu()`); refactor carefully.

## Packaging (Windows-first)
- PyInstaller build: `python -m pip install -e .[dev]` then `python build_exe.py` (Windows-only) (see [../build_exe.py](../build_exe.py)).
