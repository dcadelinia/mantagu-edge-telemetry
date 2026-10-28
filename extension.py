"""
Omniverse Kit extension stub for ManTAGU shoe telemetry.
Requires omni.ext / omni.ui at runtime inside Omniverse Kit.
This file is syntactically valid pure Python for offline import checks.
"""
from __future__ import annotations

from typing import Any, Optional


class ManTAGUTelemetryExtension:
    """Lightweight stand-in; real Kit binds omni.ext.IExt."""

    def __init__(self) -> None:
        self._window: Optional[Any] = None

    def on_startup(self, ext_id: str = "") -> None:
        print("[ManTAGU Extension] Initializing NVIDIA Inception Physical AI Layer...")
        print("[ManTAGU Extension] UI window would open inside Omniverse Kit.")
        self._window = {"title": "ManTAGU Shoe Telemetry Anchor"}

    def _on_sync_pressed(self) -> None:
        print(
            "[ManTAGU Extension] Streaming localized OpenUSD physics layers "
            "to NVIDIA Cosmos pipeline."
        )

    def on_shutdown(self) -> None:
        print("[ManTAGU Extension] Shutting down haptic data stream pipeline safely.")
        self._window = None


# Optional real Kit base if present
try:
    import omni.ext  # type: ignore

    class ManTAGUTelemetryExtensionKit(omni.ext.IExt, ManTAGUTelemetryExtension):  # type: ignore[misc]
        def on_startup(self, ext_id):  # type: ignore[no-untyped-def]
            ManTAGUTelemetryExtension.on_startup(self, ext_id)

        def on_shutdown(self):  # type: ignore[no-untyped-def]
            ManTAGUTelemetryExtension.on_shutdown(self)

except ImportError:
    pass
