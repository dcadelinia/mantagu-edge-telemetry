"""Configuration models and loaders."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field

try:
    from pydantic_settings import BaseSettings as _BaseSettings
except ImportError:  # pragma: no cover
    _BaseSettings = BaseModel  # type: ignore


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


class APIConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 2
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])


class MantaguConfig(BaseModel):
    system_name: str = "ManTAGU Edge Telemetry Network"
    edge_node_id: str = "ManTAGU-Vector-01"
    sample_rate_hz: int = 50
    imu: IMUConfig = Field(default_factory=IMUConfig)
    dead_reckoning: DeadReckoningConfig = Field(default_factory=DeadReckoningConfig)
    fusion: FusionConfig = Field(default_factory=FusionConfig)
    serial: SerialConfig = Field(default_factory=SerialConfig)
    api: APIConfig = Field(default_factory=APIConfig)


class Settings(_BaseSettings):
    """Environment-driven settings for cloud deployment."""

    mantagu_config_path: str = "config/mantagu.yaml"
    mantagu_mock_serial: bool = True
    mantagu_api_key: Optional[str] = None
    mantagu_log_level: str = "INFO"
    mantagu_s3_bucket: Optional[str] = None
    mantagu_mqtt_broker: Optional[str] = None
    mantagu_redis_url: Optional[str] = None

    def __init__(self, **data: Any):
        if not data:
            data = {
                "mantagu_config_path": os.getenv(
                    "MANTAGU_CONFIG_PATH", "config/mantagu.yaml"
                ),
                "mantagu_mock_serial": os.getenv("MANTAGU_MOCK_SERIAL", "true").lower()
                in ("1", "true", "yes"),
                "mantagu_api_key": os.getenv("MANTAGU_API_KEY") or None,
                "mantagu_log_level": os.getenv("MANTAGU_LOG_LEVEL", "INFO"),
                "mantagu_s3_bucket": os.getenv("MANTAGU_S3_BUCKET") or None,
                "mantagu_mqtt_broker": os.getenv("MANTAGU_MQTT_BROKER") or None,
                "mantagu_redis_url": os.getenv("MANTAGU_REDIS_URL") or None,
            }
        super().__init__(**data)

    class Config:
        env_prefix = ""
        case_sensitive = False


def load_config(path: Optional[str | Path] = None) -> MantaguConfig:
    cfg_path = Path(path or "config/mantagu.yaml")
    if not cfg_path.is_file():
        return MantaguConfig()
    with cfg_path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return MantaguConfig.model_validate(raw)


def load_project_identity(path: Optional[str | Path] = None) -> Dict[str, Any]:
    p = Path(path or "config.json")
    if not p.is_file():
        return {}
    with p.open(encoding="utf-8") as f:
        return json.load(f)
