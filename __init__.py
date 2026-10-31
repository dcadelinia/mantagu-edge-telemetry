"""ManTAGU Edge Telemetry — spatial sensor pipeline for smart footwear."""

__version__ = "1.0.0"
__author__ = "Odynex Axis Logistics LLC"

from mantagu.packets import HapticTelemetryPacket, parse_raw_stream
from mantagu.pipeline import ManTAGUPipeline
from mantagu.config import MantaguConfig, load_config

__all__ = [
    "HapticTelemetryPacket",
    "parse_raw_stream",
    "ManTAGUPipeline",
    "MantaguConfig",
    "load_config",
    "__version__",
]
