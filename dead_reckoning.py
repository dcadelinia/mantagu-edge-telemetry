"""Simple indoor dead-reckoning from footstep acceleration spikes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np

from mantagu.packets import HapticTelemetryPacket


@dataclass
class Pose2D:
    x: float = 0.0
    y: float = 0.0
    heading_rad: float = 0.0


@dataclass
class DeadReckoner:
    step_length_m: float = 0.72
    noise_gate_mps2: float = 1.5
    gravity: float = 9.81
    pose: Pose2D = field(default_factory=Pose2D)
    path: List[Tuple[float, float]] = field(default_factory=list)
    _last_step_ts: int = 0

    def update(self, packet: HapticTelemetryPacket) -> Pose2D:
        # vertical excess over gravity → step candidate
        vertical = abs(packet.acceleration_z) - self.gravity
        if vertical > self.noise_gate_mps2 and packet.timestamp_ms - self._last_step_ts > 250:
            self._last_step_ts = packet.timestamp_ms
            # crude heading from lateral accel bias
            self.pose.heading_rad += float(np.clip(packet.acceleration_y * 0.05, -0.2, 0.2))
            self.pose.x += self.step_length_m * float(np.cos(self.pose.heading_rad))
            self.pose.y += self.step_length_m * float(np.sin(self.pose.heading_rad))
            self.path.append((self.pose.x, self.pose.y))
        return self.pose
