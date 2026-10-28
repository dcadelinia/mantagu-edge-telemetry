from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field


class IMUConfig(BaseModel):
    gravity_mps2: float = 9.81


class DeadReckoningConfig(BaseModel):
    step_length_m: float = 0.72
    noise_gate_mps2: float = 1.5


class FusionConfig(BaseModel):
    batch_size: int = 256


class SerialConfig(BaseModel):
    port: str = "/dev/ttyUSB0"
    baud: int = 115200
    mock: bool = True


class MantaguConfig(BaseModel):
    system_name: str = "ManTAGU Edge Telemetry Network"
    edge_node_id: str = "ManTAGU-Vector-01"
    sample_rate_hz: int = 50
    imu: IMUConfig = Field(default_factory=IMUConfig)
    dead_reckoning: DeadReckoningConfig = Field(default_factory=DeadReckoningConfig)
    fusion: FusionConfig = Field(default_factory=FusionConfig)
    serial: SerialConfig = Field(default_factory=SerialConfig)


def load_config(path: Optional[str | Path] = None) -> MantaguConfig:
    cfg_path = Path(path or "config/mantagu.yaml")
    if not cfg_path.is_file():
        return MantaguConfig()
    with cfg_path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return MantaguConfig.model_validate(raw)


def load_project_identity(path: str | Path = "config.json") -> Dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))
