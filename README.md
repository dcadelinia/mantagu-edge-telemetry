# ManTAGU Edge Telemetry

Edge sensor data pipeline and spatial telemetry firmware for the **ManTAGU Smart Footwear System**, built under the **NVIDIA Inception Program** for Physical AI ground-truthing.

Developed by **Odynex Axis Logistics LLC**.

Maps surface friction, material compliance, and indoor spatial paths from human kinetic motion to bridge **Sim-to-Real** for Omniverse and foundation world models.

---

## Core architecture

1. **Firmware** (`firmware/`) — C++ sketch for ESP32/BLE soles: IMU + piezoelectric matrix → `MANTAGU_DATA:` serial stream  
2. **Data pipeline** (`src/mantagu`, `data_pipeline/`) — parse packets, dead-reckon, friction/yield fusion  
3. **Omniverse connector** — OpenUSD layout + Kit extension stub  

---

## What was fixed

| Issue | Fix |
|-------|-----|
| Python / C++ / extension sources **not valid** (indentation stripped) | Fully rewritten modules |
| Malformed paths (`requirements.txt)`, `(.github/...`) | Clean tree |
| Warp-only fusion would crash without GPU package | NumPy fallback |
| Broken README clone URL / truncated install | Correct docs + working entrypoints |

---

## Quick start

```bash
cd mantagu-edge-telemetry
pip install -r requirements.txt

PYTHONPATH=src python -m mantagu.cli --frames 5
PYTHONPATH=src python data_pipeline/ingestion.py
PYTHONPATH=src python data_pipeline/sim_warp.py
PYTHONPATH=src pytest -q
```

---

## Layout

```
src/mantagu/          packets, dead_reckoning, fusion, pipeline, cli
data_pipeline/        compatibility ingestion.py + sim_warp.py
firmware/src/main.cpp
omniverse_connector/scene_layout.usda
exts/omni.mantagu.telemetry/...
config.json  config/mantagu.yaml
```

---

## IP

Proprietary spatial intelligence pipeline of Odynex Axis Logistics LLC.  
Governed under TUTSA as noted in `config.json`. See [LICENSE](LICENSE).
