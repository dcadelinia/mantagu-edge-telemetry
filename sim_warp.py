#!/usr/bin/env python3
"""Compatibility entry — Warp/NumPy footstep fusion."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mantagu.fusion import run_gpu_sensor_fusion_batch

if __name__ == "__main__":
    run_gpu_sensor_fusion_batch(batch_size=1024, seed=0)
