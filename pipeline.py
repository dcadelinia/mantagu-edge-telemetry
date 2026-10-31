"""Ingestion pipeline — mock/real serial → parse → dead-reckon → fusion → JSON."""
from __future__ import annotations

import json
import random
import time
from typing import Any, Dict, Iterator, List, Optional

from mantagu.config import MantaguConfig, load_config
from mantagu.dead_reckoning import DeadReckoner
from mantagu.fusion import fuse_packet
from mantagu.packets import HapticTelemetryPacket, parse_raw_stream


class ManTAGUPipeline:
    def __init__(self, config: Optional[MantaguConfig] = None):
        self.config = config or load_config()
        self.reckoner = DeadReckoner(
            step_length_m=self.config.dead_reckoning.step_length_m,
            noise_gate_mps2=self.config.dead_reckoning.noise_gate_mps2,
            gravity=self.config.imu.gravity_mps2,
        )
        self.packets: List[HapticTelemetryPacket] = []
        self._last_frames: List[Dict[str, Any]] = []

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        pkt = parse_raw_stream(line)
        if pkt is None:
            return None
        self.packets.append(pkt)
        pose = self.reckoner.update(pkt)
        fusion = fuse_packet(pkt.acceleration_z, pkt.surface_compliance)
        frame = {
            **pkt.to_dict(),
            "node_id": self.config.edge_node_id,
            "pose": pose,
            "fusion": fusion,
            "export_compliance": "WTO_E_COMMERCE_2026_COMPLIANT",
        }
        self._last_frames.append(frame)
        if len(self._last_frames) > 1000:
            self._last_frames = self._last_frames[-500:]
        return frame

    def mock_line(self) -> str:
        ts = int(time.time() * 1000)
        ax = random.uniform(-2.0, 2.0)
        ay = random.uniform(-2.0, 2.0)
        az = random.uniform(9.5, 10.2)
        compliance = random.randint(1200, 3100)
        friction = random.uniform(0.15, 0.95)
        return f"MANTAGU_DATA:{ts},{ax:.3f},{ay:.3f},{az:.3f},{compliance},{friction:.3f}"

    def stream_mock(self, frames: int = 5, sleep_s: float = 0.0) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for _ in range(frames):
            line = self.mock_line()
            frame = self.parse_line(line)
            if frame:
                out.append(frame)
            if sleep_s > 0:
                time.sleep(sleep_s)
        return out

    def stream_to_sim_environment(
        self, frames: int = 5, sleep_s: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Compatibility alias used by CLI / demos."""
        return self.stream_mock(frames=frames, sleep_s=sleep_s)

    def latest(self, n: int = 10) -> List[Dict[str, Any]]:
        return self._last_frames[-n:]

    def path_json(self) -> str:
        return json.dumps(self.reckoner.path, indent=2)
