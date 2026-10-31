"""Friction / material-yield sensor fusion (Warp GPU or NumPy fallback)."""
from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np

_HAS_WARP = False
try:
    import warp as wp  # type: ignore

    wp.init()
    _HAS_WARP = True
except Exception:
    _HAS_WARP = False


def _numpy_fusion(
    accel_z: np.ndarray, pressure: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    gravity_norm = accel_z / 9.81
    friction = (pressure * 0.0003) * gravity_norm
    material_yield = pressure * 1.42
    return friction.astype(np.float32), material_yield.astype(np.float32)


if _HAS_WARP:

    @wp.kernel  # type: ignore
    def compute_footstep_physics(
        raw_accel_z: Any,
        raw_pressure: Any,
        out_friction_indices: Any,
        out_material_yield: Any,
    ):
        tid = wp.tid()
        gravity_norm = raw_accel_z[tid] / 9.81
        out_friction_indices[tid] = (raw_pressure[tid] * 0.0003) * gravity_norm
        out_material_yield[tid] = raw_pressure[tid] * 1.42


def run_gpu_sensor_fusion_batch(
    batch_size: int = 256, seed: int = 42
) -> Dict[str, Any]:
    """Run a batch fusion pass. Uses Warp if available, else NumPy."""
    rng = np.random.default_rng(seed)
    accel_z = rng.uniform(9.5, 10.2, batch_size).astype(np.float32)
    pressure = rng.uniform(1000.0, 4500.0, batch_size).astype(np.float32)

    if _HAS_WARP:
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
        friction, material_yield = _numpy_fusion(accel_z, pressure)
        backend = "numpy"

    return {
        "backend": backend,
        "batch_size": batch_size,
        "slip_index_0": float(friction[0]),
        "material_yield_0": float(material_yield[0]),
        "mean_friction": float(np.mean(friction)),
        "mean_yield": float(np.mean(material_yield)),
    }


def fuse_packet(
    accel_z: float, surface_compliance: float
) -> Dict[str, float]:
    """Single-sample fusion for live stream."""
    friction = (surface_compliance * 0.0003) * (accel_z / 9.81)
    material_yield = surface_compliance * 1.42
    return {
        "slip_index": float(friction),
        "material_yield": float(material_yield),
    }
