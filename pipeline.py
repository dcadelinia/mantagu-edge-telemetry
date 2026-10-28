"""Ingestion pipeline — mock serial stream → parse → dead-reckon → Omniverse dict."""
from __future__ import annotations

import json
import random
import time
from typing import Any, Dict, Iterator, List, Optional

from mantagu.config import MantaguConfig, load_config
from mantagu.dead_reckoning import DeadReckoner
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

    def parse_raw_stream(self, line: str) -> Optional[Dict[str, Any]]:
        pkt = parse_raw_stream(line)
        if pkt is None:
            return None
        self.packets.append(pkt)
        pose = self.reckoner.update(pkt)
        return {
            **pkt.to_dict(),
            "node_id": self.config.edge_node_id,
            "pose_x": pose.x,
            "pose_y": pose.y,
            "heading_rad": pose.heading_rad,
        }

    def mock_lines(self, n: int = 5) -> Iterator[str]:
        t0 = int(time.time() * 1000)
        for i in range(n):
            ts = t0 + i * int(1000 / max(self.config.sample_rate_hz, 1))
            ax = random.uniform(-2.0, 2.0)
            ay = random.uniform(-2.0, 2.0)
            # occasional step spikes on Z
            az = random.uniform(9.5, 10.2) if i % 2 else random.uniform(11.5, 13.0)
            compliance = random.randint(1200, 3100)
            friction = random.uniform(0.15, 0.95)
            yield (
                f"MANTAGU_DATA:{ts},{ax:.3f},{ay:.3f},{az:.3f},"
                f"{compliance},{friction:.3f}"
            )

    def stream_to_sim_environment(self, frames: int = 5, sleep_s: float = 0.0) -> List[Dict[str, Any]]:
        print(
            f"[ManTAGU] Streaming edge node {self.config.edge_node_id} "
            f"→ Omniverse layer"
        )
        out: List[Dict[str, Any]] = []
        for line in self.mock_lines(frames):
            parsed = self.parse_raw_stream(line)
            if parsed:
                print(f"[DATA PACKET SENT TO OMNIVERSE]: {json.dumps(parsed, indent=2)}")
                out.append(parsed)
            if sleep_s > 0:
                time.sleep(sleep_s)
        return out


if __name__ == "__main__":
    pipeline = ManTAGUPipeline()
    pipeline.stream_to_sim_environment(frames=5, sleep_s=0.0)
