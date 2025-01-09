import xraydb
import os
import sys

class MaterialError(Exception):
    """Base exception for material-related errors."""
    pass

class MaterialNotFoundError(MaterialError):
    """Exception raised when material is not found in xraydb."""
    pass

class InvalidThicknessError(MaterialError):
    """Exception raised when material thickness is invalid."""
    pass

def get_db_path():
    """Get the correct path to xraydb.sqlite for both development and executable"""
    if getattr(sys, 'frozen', False):
        # Running as executable
        base_path = sys._MEIPASS
        return os.path.join(base_path, 'xraydb', 'xraydb.sqlite')
    else:
        # Running in development
        return os.path.join(os.path.dirname(xraydb.__file__), 'xraydb.sqlite')

def get_material_list():
    """Get list of available materials from xraydb"""
    try:
        # Get database path
        db_path = get_db_path()
        # Create xraydb session (no need to set it explicitly)
        materials = xraydb.get_materials()  # Changed from materials_list()
        return sorted(materials)
    except Exception as e:
        print(f"Error loading materials: {str(e)}")
        return []

def find_material(name):
    """
    Find a material by name in xraydb
    Args:
        name (str): Name of the material to find
    Returns:
        dict: Material properties if found, None if not found
    """
    try:
        material = xraydb.find_material(name)
        return material
    except ValueError:
        return None

def validate_material(material_name, thickness=None):
    """
    Validate if material exists in xraydb and thickness is valid
    Args:
        material_name (str): Name of the material to validate
        thickness (float, optional): Thickness to validate
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    Raises:
        MaterialNotFoundError: If material is not found in xraydb
        InvalidThicknessError: If thickness is invalid
    """
    try:
        if not isinstance(material_name, str):
            raise MaterialError("Material name must be a string")
        
        material = find_material(material_name)
        if material is None:
            raise MaterialNotFoundError(f"Material '{material_name}' not found in database")
        
        if thickness is not None:
            if not isinstance(thickness, (int, float)):
                raise InvalidThicknessError("Thickness must be a number")
            if thickness <= 0:
                raise InvalidThicknessError("Thickness must be positive")
        
        return True, ""

    except Exception as e:
        return False, str(e)
