"""Serial packet parsing for ManTAGU sole sensors."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class HapticTelemetryPacket:
    timestamp_ms: int
    acceleration_x: float
    acceleration_y: float
    acceleration_z: float
    surface_compliance: float  # micro-Newtons scale in firmware mapping
    micro_friction_index: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_raw_stream(line: str) -> Optional[HapticTelemetryPacket]:
    """
    Expected format:
    MANTAGU_DATA:<ts>,<ax>,<ay>,<az>,<compliance>,<friction>
    """
    line = (line or "").strip()
    if not line.startswith("MANTAGU_DATA:"):
        return None
    payload = line[len("MANTAGU_DATA:") :]
    parts = payload.split(",")
    if len(parts) < 6:
        return None
    try:
        return HapticTelemetryPacket(
            timestamp_ms=int(float(parts[0])),
            acceleration_x=float(parts[1]),
            acceleration_y=float(parts[2]),
            acceleration_z=float(parts[3]),
            surface_compliance=float(parts[4]),
            micro_friction_index=float(parts[5]),
        )
    except ValueError:
        return None
