from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from mantagu.config import load_config, load_project_identity
from mantagu.fusion import run_gpu_sensor_fusion_batch
from mantagu.pipeline import ManTAGUPipeline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ManTAGU Edge Telemetry")
    parser.add_argument("--config", default=str(ROOT / "config" / "mantagu.yaml"))
    parser.add_argument("--frames", type=int, default=5)
    parser.add_argument("--fusion-batch", type=int, default=256)
    args = parser.parse_args(argv)

    identity = load_project_identity(ROOT / "config.json")
    cfg = load_config(args.config)
    print(json.dumps({"identity": identity.get("project_identity", {}), "node": cfg.edge_node_id}, indent=2))

    pipe = ManTAGUPipeline(cfg)
    packets = pipe.stream_to_sim_environment(frames=args.frames, sleep_s=0.0)
    fusion = run_gpu_sensor_fusion_batch(batch_size=args.fusion_batch, seed=1)
    print("--- fusion ---")
    print(json.dumps(fusion, indent=2))
    print("--- path points ---")
    print(json.dumps(pipe.reckoner.path, indent=2))
    return 0 if packets else 1


if __name__ == "__main__":
    raise SystemExit(main())
