from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .filter import Channel
from .units import kev_to_ev, um_to_cm


@dataclass
class TransmissionResult:
    energies_ev: np.ndarray
    transmissions: list[np.ndarray] = field(default_factory=list)
    differences: list[np.ndarray] = field(default_factory=list)


class RossFilterCalculator:
    def __init__(self):
        self.channels: list[Channel] = []

    def reset(self):
        """Reset all channels."""
        self.channels = []
        return True, "All channels reset successfully"

    def add_channel(self) -> int:
        """Add a new empty channel.
        
        Returns:
            index of the new channel
        """
        self.channels.append(Channel())
        return len(self.channels) - 1

    def remove_channel(self, channel_idx: int):
        """Remove a channel by index."""
        if 0 <= channel_idx < len(self.channels):
            self.channels.pop(channel_idx)
            return True, f"Removed Channel {channel_idx + 1}"
        return False, f"Invalid channel index {channel_idx}"

    def add_filter_to_channel(self, channel_idx: int, material: str, thickness_um: float, density: float | None = None):
        """Add a filter layer to a specific channel.

        Args:
            channel_idx: Index of the channel (0-based)
            material: xraydb material name
            thickness_um: thickness in micrometers (µm)
            density: density in g/cm^3 (optional)
        """
        if not (0 <= channel_idx < len(self.channels)):
             return False, f"Invalid channel index {channel_idx}"

        channel = self.channels[channel_idx]

        if material in ["Select Material", ""]:
            return False, f"Please select a material for Channel {channel_idx + 1}"

        try:
            thickness_cm = um_to_cm(thickness_um)
            return channel.add_filter(material, thickness_cm, density)
        except ValueError:
            return False, "Invalid thickness value"

    def remove_filter_from_channel(self, channel_idx: int, filter_idx: int):
        """Remove a filter from a specific channel."""
        if not (0 <= channel_idx < len(self.channels)):
             return False, f"Invalid channel index {channel_idx}"
        
        channel = self.channels[channel_idx]
        success, msg = channel.remove_filter(filter_idx)
        if success:
            return True, f"Removed filter from Channel {channel_idx + 1}"
        return False, msg

    def update_filter_in_channel(self, channel_idx: int, filter_idx: int, material: str, thickness_um: float, density: float | None = None):
        """Update a filter in a specific channel."""
        if not (0 <= channel_idx < len(self.channels)):
             return False, f"Invalid channel index {channel_idx}"

        channel = self.channels[channel_idx]
        try:
            thickness_cm = um_to_cm(thickness_um)
            return channel.update_filter(filter_idx, material, thickness_cm, density)
        except ValueError:
            return False, "Invalid thickness value"

    def calculate_transmission(self, energy_start_kev, energy_stop_kev, energy_step_kev):
        """Calculate transmission for all channels and sequential differences.

        GUI inputs are in keV; internal computations are in eV.
        """
        try:
            start_ev = float(kev_to_ev(float(energy_start_kev)))
            stop_ev = float(kev_to_ev(float(energy_stop_kev)))
            step_ev = float(kev_to_ev(float(energy_step_kev)))

            if start_ev >= stop_ev:
                return False, "Start energy must be less than stop energy"
            if step_ev <= 0:
                return False, "Step size must be positive"
            if start_ev < 0:
                return False, "Start energy must be positive"

            if not self.channels:
                return False, "No channels added."

            energies = np.arange(start_ev, stop_ev + step_ev, step_ev)
            
            transmissions = []
            for channel in self.channels:
                transmissions.append(channel.calculate_transmission(energies))
            
            differences = []
            # Calculate sequential differences: Ch1-Ch2, Ch2-Ch3, etc.
            for i in range(len(transmissions) - 1):
                diff = np.abs(transmissions[i] - transmissions[i+1])
                differences.append(diff)

            result = TransmissionResult(
                energies_ev=energies,
                transmissions=transmissions,
                differences=differences
            )

            return True, result

        except ValueError:
            return False, "Invalid energy values"
        except Exception as e:
            return False, f"Calculation error: {str(e)}"
