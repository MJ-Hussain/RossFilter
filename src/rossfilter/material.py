import os
import sys

import xraydb


class MaterialError(Exception):
    """Base exception for material-related errors."""


class MaterialNotFoundError(MaterialError):
    """Raised when a material cannot be found in xraydb."""


class InvalidThicknessError(MaterialError):
    """Raised when a thickness is invalid."""


def get_db_path() -> str:
    """Return path to xraydb.sqlite for dev and frozen executables."""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
        return os.path.join(base_path, "xraydb", "xraydb.sqlite")
    return os.path.join(os.path.dirname(xraydb.__file__), "xraydb.sqlite")


def get_material_list() -> list[str]:
    """Get list of available materials from xraydb."""
    try:
        return sorted(xraydb.get_materials())
    except Exception as e:
        print(f"Error loading materials: {str(e)}")
        return []


def find_material(name: str):
    try:
        return xraydb.find_material(name)
    except ValueError:
        return None


def validate_material(material_name: str, thickness=None):
    """Validate if material exists in xraydb and thickness is valid.

    Returns:
        (is_valid: bool, error_message: str)
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
