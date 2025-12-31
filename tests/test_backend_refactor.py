import numpy as np
from rossfilter.calculator import RossFilterCalculator

def test_backend_refactor():
    calc = RossFilterCalculator()
    
    # Test adding channels
    idx1 = calc.add_channel()
    idx2 = calc.add_channel()
    assert idx1 == 0
    assert idx2 == 1
    assert len(calc.channels) == 2
    
    # Test adding filters to channels
    # Assuming 'Be' and 'Al' are valid materials in xraydb (they usually are)
    success, msg = calc.add_filter_to_channel(0, 'Be', 10.0) # 10 um Be
    assert success, f"Failed to add filter to channel 0: {msg}"
    
    success, msg = calc.add_filter_to_channel(1, 'Al', 5.0) # 5 um Al
    assert success, f"Failed to add filter to channel 1: {msg}"
    
    # Test calculation
    success, result = calc.calculate_transmission(1.0, 10.0, 1.0) # 1-10 keV
    assert success, f"Calculation failed: {result}"
    
    # Verify result structure
    assert hasattr(result, 'energies_ev')
    assert hasattr(result, 'transmissions')
    assert hasattr(result, 'differences')
    
    assert len(result.transmissions) == 2
    assert len(result.differences) == 1 # 2 channels -> 1 difference
    
    print("Backend refactor test passed!")

if __name__ == "__main__":
    test_backend_refactor()
