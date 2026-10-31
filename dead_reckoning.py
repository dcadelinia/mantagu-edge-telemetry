"""Indoor dead-reckoning from sole IMU / step events."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from mantagu.packets import HapticTelemetryPacket


@dataclass
class DeadReckoner:
    step_length_m: float = 0.72
    noise_gate_mps2: float = 1.5
    gravity: float = 9.81
    path: List[Dict[str, float]] = field(default_factory=list)
    _last_ts: int = 0
    _x: float = 0.0
    _y: float = 0.0
    _heading: float = 0.0

    def update(self, pkt: HapticTelemetryPacket) -> Dict[str, Any]:
        """Update pose from a telemetry packet. Returns current pose dict."""
        # Simple magnitude of horizontal accel as step detector proxy
        horiz = (pkt.acceleration_x**2 + pkt.acceleration_y**2) ** 0.5
        step = horiz > self.noise_gate_mps2

        if step and (pkt.timestamp_ms - self._last_ts) > 200:
            # Advance along current heading
            import math

            self._x += self.step_length_m * math.cos(self._heading)
            self._y += self.step_length_m * math.sin(self._heading)
            # Crude yaw from lateral accel
            self._heading += pkt.acceleration_y * 0.05
            self._last_ts = pkt.timestamp_ms

        pose = {
            "x_m": round(self._x, 4),
            "y_m": round(self._y, 4),
            "heading_rad": round(self._heading, 4),
            "step": step,
            "timestamp_ms": pkt.timestamp_ms,
        }
        self.path.append(pose)
        # Keep path bounded for long-running edge nodes
        if len(self.path) > 10_000:
            self.path = self.path[-5_000:]
        return pose
