import numpy as np
from typing import Union

def kev_to_ev(energy_kev: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    return np.array(energy_kev) * 1e3 if isinstance(energy_kev, (list, tuple, np.ndarray)) else float(energy_kev) * 1e3


def um_to_cm(thickness_um: float) -> float:
    return float(thickness_um) * 1e-4
