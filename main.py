from gui import RossFilterGUI
from filter import Filter
from numpy import arange, abs

class RossFilterCalculator:
    def __init__(self):
        self.filter1 = Filter()
        self.filter2 = Filter()
        
    def reset(self):
        """Reset both filters to empty state"""
        self.filter1 = Filter()
        self.filter2 = Filter()
        return True, "Filters reset successfully"
        
    def add_material_to_filter(self, filter_num, material, thickness_um):
        """
        Add material to specified filter
        Args:
            filter_num (int): 1 or 2 to specify filter
            material (str): Material name
            thickness_um (float): Thickness in micrometers
        Returns:
            tuple: (success, message)
        """
        filter_instance = self.filter1 if filter_num == 1 else self.filter2
        
        # Skip if material is not selected
        if material in ["Select Material", ""]:
            return False, f"Please select a material for Filter {filter_num}"

        try:
            # Convert thickness from µm to cm
            thickness = float(thickness_um) * 1e-4
            return filter_instance.add_material(material, thickness)
                
        except ValueError:
            return False, "Invalid thickness value"

    def calculate_transmission(self, energy_start, energy_stop, energy_step):
        """
        Calculate transmission for both filters across energy range
        """
        try:
            # Validate energy inputs
            start = float(energy_start)*1E3
            stop = float(energy_stop)*1E3
            step = float(energy_step)*1E3
            
            if start >= stop:
                return False, "Start energy must be less than stop energy"
            if step <= 0:
                return False, "Step size must be positive"
            if start < 0:
                return False, "Start energy must be positive"
            
            # Check if any filters are added
            filter1_empty = len(self.filter1.materials) == 0
            filter2_empty = len(self.filter2.materials) == 0
            
            if filter1_empty and filter2_empty:
                return False, "No filters added. Please add at least one filter."
            
            # Create energy array
            energies = arange(start, stop + step, step)
            
            # Calculate transmissions based on available filters
            result = {'energies': energies}
            
            if not filter1_empty:
                result['transmission1'] = self.filter1.calculate_transmission(energies)
            
            if not filter2_empty:
                result['transmission2'] = self.filter2.calculate_transmission(energies)
            
            # Calculate difference only if both filters are present
            if not filter1_empty and not filter2_empty:
                result['difference'] = self.calculate_difference(
                    result['transmission1'], 
                    result['transmission2']
                )
            
            return True, result
            
        except ValueError:
            return False, "Invalid energy values"
        except Exception as e:
            return False, f"Calculation error: {str(e)}"

    def calculate_difference(self, trans1, trans2):
        """
        Calculate difference between two transmissions
        
        Args:
            trans1 (numpy.ndarray): First transmission array
            trans2 (numpy.ndarray): Second transmission array
            
        Returns:
            numpy.ndarray: Absolute difference between transmissions
        """
        return abs(trans1 - trans2)

    def plot_transmission(self, ax):
        """Plot transmission data on the given axes"""
        # Clear previous plot
        ax.clear()
        
        # Set labels and grid
        ax.set_xlabel('Energy (keV)')
        ax.set_ylabel('Transmission')
        ax.set_title('Ross Filter Transmission')
        ax.grid(True)

def main():
    calculator = RossFilterCalculator()
    app = RossFilterGUI(calculator)
    app.run()

if __name__ == "__main__":
    main()
