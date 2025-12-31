from dataclasses import dataclass
import numpy as np
import xraydb

from .material import (
    InvalidThicknessError,
    MaterialNotFoundError,
    validate_material,
)


@dataclass
class Filter:
    """A single filter layer consisting of a material and thickness."""
    material: str
    thickness: float  # cm
    density: float | None = None  # g/cm^3


class Channel:
    """A channel consisting of a stack of filters."""
    def __init__(self):
        self.filters: list[Filter] = []

    def add_filter(self, material: str, thickness_cm: float, density: float | None = None):
        """Add a filter layer to the channel.

        Returns:
            (success: bool, message: str)
        """
        try:
            is_valid, error_message = validate_material(material, thickness_cm)
            if not is_valid:
                return False, error_message

            self.filters.append(Filter(material, thickness_cm, density))
            return True, ""

        except MaterialNotFoundError as e:
            return False, f"Material error: {str(e)}"
        except InvalidThicknessError as e:
            return False, f"Thickness error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def remove_filter(self, index: int):
        """Remove a filter by index."""
        if 0 <= index < len(self.filters):
            self.filters.pop(index)
            return True, ""
        return False, "Invalid filter index"

    def update_filter(self, index: int, material: str, thickness_cm: float, density: float | None = None):
        """Update an existing filter."""
        if not (0 <= index < len(self.filters)):
            return False, "Invalid filter index"

        try:
            is_valid, error_message = validate_material(material, thickness_cm)
            if not is_valid:
                return False, error_message

            self.filters[index] = Filter(material, thickness_cm, density)
            return True, ""
        except Exception as e:
            return False, f"Update error: {str(e)}"

    def calculate_transmission(self, energy_ev):
        energy_ev = np.array(energy_ev, dtype=np.float64)
        transmission = np.ones_like(energy_ev, dtype=np.float64)

        for filter_layer in self.filters:
            mu = np.array([xraydb.material_mu(filter_layer.material, e, density=filter_layer.density) for e in energy_ev])
            transmission *= np.exp(-mu * filter_layer.thickness)

        return transmission

    def calculate_single_filter(self, index: int, energy_ev):
        energy_ev = np.array(energy_ev, dtype=np.float64)
        if not (0 <= index < len(self.filters)):
            raise IndexError("Invalid filter index")

        target = self.filters[index]
        mu = np.array([xraydb.material_mu(target.material, e, density=target.density) for e in energy_ev])
        return np.exp(-mu * target.thickness)

    @staticmethod
    def difference(transmission1, transmission2):
        return np.abs(transmission1 - transmission2)
