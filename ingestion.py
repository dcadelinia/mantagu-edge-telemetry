#!/usr/bin/env python3
"""Compatibility entry — ManTAGU ingestion pipeline."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mantagu.pipeline import ManTAGUPipeline

if __name__ == "__main__":
    ManTAGUPipeline().stream_to_sim_environment(frames=5, sleep_s=0.0)
