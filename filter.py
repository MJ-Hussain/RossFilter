import numpy as np
import xraydb
from material import validate_material, MaterialError, MaterialNotFoundError, InvalidThicknessError, get_db_path

class Filter:
    def __init__(self):
        self.materials = []
        self.thicknesses = []
        # No need to set database path explicitly
        # xraydb handles this internally
    
    def add_material(self, material, thickness):
        """
        Add material layer to the filter.
        
        Args:
            material (str): Material name from xraydb
            thickness (float): Thickness in cm
            
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        try:
            # Validate material and thickness
            is_valid, error_message = validate_material(material, thickness)
            if not is_valid:
                return False, error_message

            self.materials.append(material)
            self.thicknesses.append(thickness)
            return True, ""

        except MaterialNotFoundError as e:
            return False, f"Material error: {str(e)}"
        except InvalidThicknessError as e:
            return False, f"Thickness error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def calculate_transmission(self, energy):
        # Convert energy to numpy array if it isn't already
        energy = np.array(energy, dtype=np.float64)
        # Initialize transmission array with ones as float64
        transmission = np.ones_like(energy, dtype=np.float64)
        
        for material, thickness in zip(self.materials, self.thicknesses):
            # Get mass attenuation coefficient
            mu = np.array([xraydb.material_mu(material, e) for e in energy])
            # Calculate transmission
            transmission *= np.exp(-mu * thickness)
        
        return transmission

    @staticmethod
    def difference(transmission1, transmission2):
        """
        Calculate the difference between two transmissions.
        
        Args:
            transmission1 (numpy.ndarray): First transmission array
            transmission2 (numpy.ndarray): Second transmission array
            
        Returns:
            numpy.ndarray: Difference between transmissions
        """
        return np.abs(transmission1 - transmission2)