# ManTAGU Edge Telemetry Architecture

| Layer | Path | Role |
|-------|------|------|
| Firmware | `firmware/src/main.cpp` | ESP32 sole IMU + piezo stream |
| Packets | `mantagu.packets` | `MANTAGU_DATA:` parser |
| Dead reckoning | `mantagu.dead_reckoning` | Indoor step path |
| Fusion | `mantagu.fusion` | Friction / yield (Warp or NumPy) |
| Pipeline | `mantagu.pipeline` | Mock serial → Omniverse JSON |
| OpenUSD | `omniverse_connector/scene_layout.usda` | Foot contact proxy |
| Kit ext | `exts/omni.mantagu.telemetry/...` | Omniverse UI stub |
