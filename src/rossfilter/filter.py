import numpy as np
import xraydb

from .material import (
    InvalidThicknessError,
    MaterialNotFoundError,
    validate_material,
)


class Filter:
    def __init__(self):
        self.materials: list[str] = []
        self.thicknesses: list[float] = []  # cm

    def add_material(self, material: str, thickness_cm: float):
        """Add a material layer to the filter.

        Returns:
            (success: bool, message: str)
        """
        try:
            is_valid, error_message = validate_material(material, thickness_cm)
            if not is_valid:
                return False, error_message

            self.materials.append(material)
            self.thicknesses.append(thickness_cm)
            return True, ""

        except MaterialNotFoundError as e:
            return False, f"Material error: {str(e)}"
        except InvalidThicknessError as e:
            return False, f"Thickness error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def calculate_transmission(self, energy_ev):
        energy_ev = np.array(energy_ev, dtype=np.float64)
        transmission = np.ones_like(energy_ev, dtype=np.float64)

        for material, thickness_cm in zip(self.materials, self.thicknesses):
            mu = np.array([xraydb.material_mu(material, e) for e in energy_ev])
            transmission *= np.exp(-mu * thickness_cm)

        return transmission

    @staticmethod
    def difference(transmission1, transmission2):
        return np.abs(transmission1 - transmission2)
