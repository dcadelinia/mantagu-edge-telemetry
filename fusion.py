"""Footstep physics fusion — Warp GPU when available, NumPy otherwise."""
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np

try:
    import warp as wp

    WARP_AVAILABLE = True
except ImportError:
    WARP_AVAILABLE = False
    wp = None  # type: ignore


def _numpy_fusion(
    accel_z: np.ndarray, pressure: np.ndarray, gravity: float = 9.81
) -> Tuple[np.ndarray, np.ndarray]:
    gravity_norm = accel_z / gravity
    friction = (pressure * 0.0003) * gravity_norm
    material_yield = pressure * 1.42
    return friction.astype(np.float32), material_yield.astype(np.float32)


if WARP_AVAILABLE:

    @wp.kernel
    def compute_footstep_physics(
        raw_accel_z: wp.array(dtype=float),
        raw_pressure: wp.array(dtype=float),
        out_friction_indices: wp.array(dtype=float),
        out_material_yield: wp.array(dtype=float),
    ):
        tid = wp.tid()
        gravity_norm = raw_accel_z[tid] / 9.81
        out_friction_indices[tid] = (raw_pressure[tid] * 0.0003) * gravity_norm
        out_material_yield[tid] = raw_pressure[tid] * 1.42


def run_gpu_sensor_fusion_batch(
    batch_size: int = 1024, seed: int = 0
) -> Dict[str, float]:
    """
    Evaluate foot-to-ground friction / yield indices for a batch of samples.
    Uses NVIDIA Warp when installed; otherwise NumPy.
    """
    rng = np.random.default_rng(seed)
    accel_z = rng.uniform(9.5, 10.2, batch_size).astype(np.float32)
    pressure = rng.uniform(1000.0, 4500.0, batch_size).astype(np.float32)

    if WARP_AVAILABLE:
        assert wp is not None
        wp.init()
        print(
            f"[*] Launching Parallel CUDA Inferences on {batch_size} sensor channels via NVIDIA Warp..."
        )
        accel_z_gpu = wp.array(accel_z, dtype=float)
        pressure_gpu = wp.array(pressure, dtype=float)
        friction_gpu = wp.empty(shape=batch_size, dtype=float)
        yield_gpu = wp.empty(shape=batch_size, dtype=float)
        wp.launch(
            kernel=compute_footstep_physics,
            dim=batch_size,
            inputs=[accel_z_gpu, pressure_gpu, friction_gpu, yield_gpu],
        )
        wp.synchronize()
        friction = friction_gpu.numpy()
        material_yield = yield_gpu.numpy()
        backend = "warp"
    else:
        print(
            f"[*] Warp not installed — running NumPy fusion on {batch_size} channels..."
        )
        friction, material_yield = _numpy_fusion(accel_z, pressure)
        backend = "numpy"

    print(
        "[+] Sensor Fusion Batch complete. Multi-channel physics arrays optimized for OpenUSD serialization."
    )
    print(f"Sample Calculated Slip Index (Channel 0): {friction[0]:.4f}")
    return {
        "backend": backend,
        "batch_size": batch_size,
        "slip_index_0": float(friction[0]),
        "material_yield_0": float(material_yield[0]),
        "mean_friction": float(np.mean(friction)),
    }


if __name__ == "__main__":
    run_gpu_sensor_fusion_batch()
