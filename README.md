# ManTAGU Edge Telemetry

**Production-ready** edge sensor data pipeline and spatial telemetry for the **ManTAGU Smart Footwear System**, built under the **NVIDIA Inception Program** for Physical AI ground-truthing.

Developed by **Odynex Axis Logistics LLC**.

Maps surface friction, material compliance, and indoor spatial paths from human kinetic motion to bridge **Sim-to-Real** for Omniverse and foundation world models.

---

## What this package gives you

| Layer | Path | Role |
|-------|------|------|
| Firmware | `firmware/src/main.cpp` | ESP32 sole IMU + piezo → `MANTAGU_DATA:` stream |
| Packets / fusion / dead-reckoning | `src/mantagu/` | Parse, pose, friction/yield |
| **Cloud API** | `src/mantagu/api.py` | FastAPI: ingest, mock stream, path, batch fusion |
| OpenUSD | `omniverse-connector/scene_layout.usda` | Foot-contact proxy for Omniverse |
| Kit extension | `exts/omni.mantagu.telemetry/` | Omniverse UI stub |
| **Deploy** | `Dockerfile`, `docker-compose.yml`, `deploy/*` | Any major cloud, one command |

---

## Quick start (local)

```bash
# Python 3.10+
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Demo pipeline
mantagu --frames 5

# API (dev)
uvicorn mantagu.api:app --reload --port 8080
# → http://localhost:8080/docs
# → http://localhost:8080/health
```

### Docker (recommended for any cloud)

```bash
docker compose up --build -d
curl http://localhost:8080/health
```

Optional API key:

```bash
export MANTAGU_API_KEY=your-secret
docker compose up --build -d
curl -H "X-API-Key: your-secret" http://localhost:8080/v1/latest
```

---

## API surface

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | no | Liveness |
| GET | `/ready` | no | Readiness |
| GET | `/v1/identity` | key* | Project identity |
| GET | `/v1/config` | key* | Runtime config |
| POST | `/v1/ingest` | key* | Body `{ "line": "MANTAGU_DATA:..." }` |
| POST | `/v1/stream/mock` | key* | Generate mock frames |
| GET | `/v1/latest?n=10` | key* | Recent frames |
| GET | `/v1/path` | key* | Dead-reckoned path |
| POST | `/v1/fusion/batch` | key* | Batch friction/yield |

\* If `MANTAGU_API_KEY` is set, send header `X-API-Key`. If unset, endpoints are open (fine for private networks / demos).

---

## Seamless global deploy (doable prices)

All of these run the same Docker image. Pick one; costs are approximate US list (2025–2026) for a small always-on or scale-to-zero service.

| Platform | How | Typical monthly cost (small footprint) | Notes |
|----------|-----|----------------------------------------|--------|
| **Fly.io** | `./scripts/deploy.sh fly` or `fly deploy --config deploy/fly.toml` | **~$0–7** (shared-cpu-1x 256MB, auto-stop) | True multi-region edge; great fit |
| **Render** | Connect repo + `deploy/render.yaml` | **~$0–7** free tier / Starter | Simple blueprint |
| **Railway** | `railway up` | **~$5–15** | Usage-based |
| **Google Cloud Run** | `./scripts/deploy.sh gcp` | **~$0–10** (scale-to-zero) | Global, pay per request |
| **AWS App Runner / ECS Fargate** | Push image to ECR, create service | **~$5–25** | Use provided Dockerfile |
| **Azure Container Apps** | Deploy image | **~$0–15** | Scale-to-zero |
| **DigitalOcean App Platform** | Dockerfile deploy | **~$5–12** | Simple |
| **Any Kubernetes** | `kubectl apply -f deploy/k8s/deployment.yaml` | cluster cost only | 2 replicas, 128–512Mi |

**Recommended default for global + cheap:** **Fly.io** or **Cloud Run** (scale-to-zero → near $0 when idle).

### Suggested subscription tiers (product)

Use these as SaaS pricing if you expose the API commercially:

| Tier | Price (suggested) | Limits | Backend |
|------|-------------------|--------|---------|
| **Hobby** | Free / $0 | Mock stream, 1k frames/day, single region | Fly free / Cloud Run free tier |
| **Starter** | **$19–29 / mo** | 50k frames/day, API key, 1 region | 1× shared VM or scale-to-zero |
| **Pro** | **$79–99 / mo** | 1M frames/day, multi-region, Redis path cache | 2 regions + Redis |
| **Enterprise** | Custom | Dedicated nodes, Omniverse sync, SLAs | K8s / private cloud |

These map cleanly onto the Docker image + optional Redis (`docker compose --profile full`).

---

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MANTAGU_CONFIG_PATH` | `config/mantagu.yaml` | Config file |
| `MANTAGU_MOCK_SERIAL` | `true` | Use mock sensor stream |
| `MANTAGU_API_KEY` | (empty) | Require `X-API-Key` if set |
| `MANTAGU_LOG_LEVEL` | `INFO` | Logging |
| `PORT` | `8080` | HTTP port (cloud platforms often inject this) |

---

## Layout

```
src/mantagu/          packages: packets, dead_reckoning, fusion, pipeline, api, cli
config/               mantagu.yaml
config.json           project identity / compliance
firmware/src/         ESP32 Arduino sketch
omniverse-connector/  OpenUSD scene
exts/                 Omniverse Kit extension stub
deploy/               fly.toml, render.yaml, railway.json, cloudbuild.yaml, k8s/
scripts/deploy.sh     one-command helpers
Dockerfile            multi-stage production image
docker-compose.yml    local / single-host
```

---

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```

---

## IP & license

Proprietary spatial intelligence pipeline of **Odynex Axis Logistics LLC**.  
Governed under TUTSA as noted in `config.json`. Source form under **MPL-2.0** (see `LICENSE`).

---

## One-line global deploy (example: Fly)

```bash
fly launch --config deploy/fly.toml --copy-config --yes
fly secrets set MANTAGU_API_KEY=change-me
fly deploy --config deploy/fly.toml
```

Then open the assigned `*.fly.dev` URL → `/docs`.

---

## Live payments (Stripe → your bank)

See **[BILLING.md](BILLING.md)** for the full checklist.

Recommended: Stripe Checkout + bank payout. Enter routing `091017138` and account `692101680084` **only** in the Stripe Dashboard (Settings → Payouts). Never put them in code or git.

API endpoints: `GET /v1/billing/tiers`, `POST /v1/billing/checkout`, `POST /v1/billing/portal`, `POST /v1/billing/webhook`.
