"""CLI entrypoint for local demos and edge nodes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mantagu import __version__
from mantagu.config import load_config, load_project_identity
from mantagu.fusion import run_gpu_sensor_fusion_batch
from mantagu.pipeline import ManTAGUPipeline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ManTAGU Edge Telemetry CLI",
        prog="mantagu",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--config",
        default="config/mantagu.yaml",
        help="Path to YAML config",
    )
    parser.add_argument("--frames", type=int, default=5, help="Mock stream frames")
    parser.add_argument("--fusion-batch", type=int, default=256)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only")
    args = parser.parse_args(argv)

    root = Path.cwd()
    identity = load_project_identity(root / "config.json")
    cfg = load_config(args.config)

    if not args.json:
        print(
            json.dumps(
                {
                    "identity": identity.get("project_identity", {}),
                    "node": cfg.edge_node_id,
                    "version": __version__,
                },
                indent=2,
            )
        )

    pipe = ManTAGUPipeline(cfg)
    packets = pipe.stream_to_sim_environment(frames=args.frames, sleep_s=0.0)
    fusion = run_gpu_sensor_fusion_batch(batch_size=args.fusion_batch, seed=1)

    out = {
        "frames": packets,
        "fusion": fusion,
        "path": pipe.reckoner.path,
    }
    if args.json:
        print(json.dumps(out))
    else:
        print("--- fusion ---")
        print(json.dumps(fusion, indent=2))
        print("--- path points ---")
        print(json.dumps(pipe.reckoner.path, indent=2))
    return 0 if packets else 1


if __name__ == "__main__":
    raise SystemExit(main())
