"""FastAPI service for cloud / edge deployment."""
from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mantagu import __version__
from mantagu.config import Settings, load_config, load_project_identity
from mantagu.fusion import run_gpu_sensor_fusion_batch
from mantagu.pipeline import ManTAGUPipeline

settings = Settings()
_pipeline: Optional[ManTAGUPipeline] = None
_identity: Dict[str, Any] = {}


def get_pipeline() -> ManTAGUPipeline:
    global _pipeline
    if _pipeline is None:
        cfg = load_config(settings.mantagu_config_path)
        if settings.mantagu_mock_serial:
            cfg.serial.mock = True
        _pipeline = ManTAGUPipeline(cfg)
    return _pipeline


def require_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    expected = settings.mantagu_api_key or os.getenv("MANTAGU_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _identity
    _identity = load_project_identity("config.json")
    get_pipeline()
    yield


app = FastAPI(
    title="ManTAGU Edge Telemetry API",
    description="Spatial telemetry & sensor fusion for ManTAGU Smart Footwear (NVIDIA Inception).",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IngestBody(BaseModel):
    line: str = Field(..., description="Raw serial line, e.g. MANTAGU_DATA:...")


class MockStreamBody(BaseModel):
    frames: int = Field(5, ge=1, le=500)
    sleep_s: float = Field(0.0, ge=0.0, le=2.0)


class FusionBody(BaseModel):
    batch_size: int = Field(256, ge=1, le=8192)
    seed: int = 42


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "version": __version__,
        "service": "mantagu-edge-telemetry",
    }


@app.get("/ready")
def ready() -> Dict[str, str]:
    get_pipeline()
    return {"status": "ready"}


@app.get("/v1/identity")
def identity(_: None = Depends(require_api_key)) -> Dict[str, Any]:
    return _identity or {"project_identity": {"system_name": "ManTAGU Edge Telemetry Network"}}


@app.get("/v1/config")
def config_endpoint(_: None = Depends(require_api_key)) -> Dict[str, Any]:
    pipe = get_pipeline()
    return pipe.config.model_dump()


@app.post("/v1/ingest")
def ingest(body: IngestBody, _: None = Depends(require_api_key)) -> Dict[str, Any]:
    pipe = get_pipeline()
    frame = pipe.parse_line(body.line)
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid MANTAGU_DATA line")
    return frame


@app.post("/v1/stream/mock")
def stream_mock(body: MockStreamBody, _: None = Depends(require_api_key)) -> Dict[str, Any]:
    pipe = get_pipeline()
    frames = pipe.stream_mock(frames=body.frames, sleep_s=body.sleep_s)
    return {"count": len(frames), "frames": frames}


@app.get("/v1/latest")
def latest(
    n: int = Query(10, ge=1, le=100),
    _: None = Depends(require_api_key),
) -> List[Dict[str, Any]]:
    return get_pipeline().latest(n)


@app.get("/v1/path")
def path(_: None = Depends(require_api_key)) -> Dict[str, Any]:
    pipe = get_pipeline()
    return {"points": pipe.reckoner.path, "count": len(pipe.reckoner.path)}


@app.post("/v1/fusion/batch")
def fusion_batch(body: FusionBody, _: None = Depends(require_api_key)) -> Dict[str, Any]:
    return run_gpu_sensor_fusion_batch(batch_size=body.batch_size, seed=body.seed)


# --- Billing (Stripe) — bank payouts configured only in Stripe Dashboard ---
@app.get("/v1/billing/tiers")
def billing_tiers() -> Dict[str, Any]:
    from mantagu.billing import list_tiers

    return {"tiers": list_tiers()}


@app.post("/v1/billing/checkout")
def billing_checkout(body: Dict[str, Any]) -> Dict[str, Any]:
    """Start a paid subscription. Returns Stripe Checkout URL."""
    from mantagu.billing import CheckoutRequest, create_checkout_session

    try:
        req = CheckoutRequest.model_validate(body)
        return create_checkout_session(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/v1/billing/portal")
def billing_portal(body: Dict[str, Any]) -> Dict[str, Any]:
    """Customer portal: update card, cancel, invoices."""
    from mantagu.billing import PortalRequest, create_customer_portal

    try:
        req = PortalRequest.model_validate(body)
        return create_customer_portal(req)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/v1/billing/webhook")
async def billing_webhook(request: Request) -> Dict[str, str]:
    """Stripe webhooks — Dashboard → https://YOUR_HOST/v1/billing/webhook"""
    from mantagu.billing import construct_webhook_event, handle_webhook_event

    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = construct_webhook_event(payload, sig)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}") from e
    return handle_webhook_event(event)


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "service": "ManTAGU Edge Telemetry",
        "docs": "/docs",
        "health": "/health",
        "billing_tiers": "/v1/billing/tiers",
    }
