from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .filter import Filter
from .units import kev_to_ev, um_to_cm


@dataclass
class TransmissionResult:
    energies_ev: np.ndarray
    transmission1: np.ndarray | None = None
    transmission2: np.ndarray | None = None
    difference: np.ndarray | None = None


class RossFilterCalculator:
    def __init__(self):
        self.filter1 = Filter()
        self.filter2 = Filter()

    def reset(self):
        """Reset both filters to empty state."""
        self.filter1 = Filter()
        self.filter2 = Filter()
        return True, "Filters reset successfully"

    def add_material_to_filter(self, filter_num: int, material: str, thickness_um: float):
        """Add a layer to one of the two filters.

        Args:
            filter_num: 1 or 2
            material: xraydb material name
            thickness_um: thickness in micrometers (µm)
        """
        filter_instance = self.filter1 if filter_num == 1 else self.filter2

        if material in ["Select Material", ""]:
            return False, f"Please select a material for Filter {filter_num}"

        try:
            thickness_cm = um_to_cm(thickness_um)
            return filter_instance.add_material(material, thickness_cm)
        except ValueError:
            return False, "Invalid thickness value"

    def calculate_transmission(self, energy_start_kev, energy_stop_kev, energy_step_kev):
        """Calculate transmission for available filters across an energy range.

        GUI inputs are in keV; internal computations are in eV.
        """
        try:
            start_ev = kev_to_ev(float(energy_start_kev))
            stop_ev = kev_to_ev(float(energy_stop_kev))
            step_ev = kev_to_ev(float(energy_step_kev))

            if start_ev >= stop_ev:
                return False, "Start energy must be less than stop energy"
            if step_ev <= 0:
                return False, "Step size must be positive"
            if start_ev < 0:
                return False, "Start energy must be positive"

            filter1_empty = len(self.filter1.materials) == 0
            filter2_empty = len(self.filter2.materials) == 0
            if filter1_empty and filter2_empty:
                return False, "No filters added. Please add at least one filter."

            energies = np.arange(start_ev, stop_ev + step_ev, step_ev, dtype=np.float64)
            result: dict[str, object] = {"energies": energies}

            if not filter1_empty:
                result["transmission1"] = self.filter1.calculate_transmission(energies)
            if not filter2_empty:
                result["transmission2"] = self.filter2.calculate_transmission(energies)
            if not filter1_empty and not filter2_empty:
                result["difference"] = np.abs(
                    np.asarray(result["transmission1"]) - np.asarray(result["transmission2"])
                )

            return True, result

        except ValueError:
            return False, "Invalid energy values"
        except Exception as e:
            return False, f"Calculation error: {str(e)}"
