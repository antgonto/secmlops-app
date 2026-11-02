"""fraud-clf serving API.

Startup ("reads model to load", Lab 6.1): verify checksum + Cosign signature BEFORE loading.
Any failure — mismatch, bad signature, missing verifier, timeout — exits with MODEL-LOAD-DENIED.
Contract (Labs 11-12): POST /api/predict {"instances": [[f1,f2,f3,f4], ...]}
                       -> {"probabilities": [[p0,p1], ...], "model": "fraud-clf", "version": "..."}
"""
import hashlib
import os
import subprocess
import sys
from typing import List

from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.fraudclf.model import FEATURES, FraudModel

MODEL_PATH = os.environ.get("MODEL_PATH", "model/model.safetensors")
MODEL_VERSION = os.environ.get("MODEL_VERSION", "dev")
VERIFY = os.environ.get("VERIFY_MODEL", "true").lower() == "true"
MAX_BATCH = int(os.environ.get("MAX_BATCH", "256"))
ENV = os.environ.get("ENV", "dev")
RATE_LIMIT = os.environ.get("RATE_LIMIT", "200/hour")   # per identity (Lab 12.2)


def identity(request: Request) -> str:
    """Pomerium forwards the authenticated identity as a claim header; fall back to client IP."""
    return request.headers.get("x-pomerium-claim-email") or get_remote_address(request)


limiter = Limiter(key_func=identity, default_limits=[])
REQUESTS = Counter("inference_requests_total", "Prediction requests", ["identity", "status"])


def verify_artifact() -> None:
    """Checksum first (cheap; works without the verifier), then cosign. Fail closed on anything."""
    sig, pub, sha = MODEL_PATH + ".sig", os.environ.get("COSIGN_PUB", "cosign.pub"), MODEL_PATH + ".sha256"
    if not (os.path.exists(sig) and os.path.exists(pub) and os.path.exists(sha)):
        sys.exit("MODEL-LOAD-DENIED: signature, public key, or checksum file missing")
    expected = open(sha).read().split()[0]
    actual = hashlib.sha256(open(MODEL_PATH, "rb").read()).hexdigest()
    if expected != actual:
        sys.exit("MODEL-LOAD-DENIED: checksum mismatch")
    try:
        cmd = ["cosign", "verify-blob", "--insecure-ignore-tlog", "--key", pub, "--signature", sig, MODEL_PATH]
        r = subprocess.run(cmd, capture_output=True, timeout=60)
    except FileNotFoundError:
        sys.exit("MODEL-LOAD-DENIED: cosign not available; refusing to load an unverified model")
    except subprocess.TimeoutExpired:
        sys.exit("MODEL-LOAD-DENIED: signature verification timed out")
    if r.returncode != 0:
        sys.exit(f"MODEL-LOAD-DENIED: signature verification failed: {r.stderr.decode()[:200]}")
    print("MODEL-LOAD-ALLOWED: checksum and signature verified")


if VERIFY:
    verify_artifact()
model = FraudModel(MODEL_PATH)

app = FastAPI(title="fraud-clf", version=MODEL_VERSION,
              docs_url=None if ENV == "prod" else "/docs",
              openapi_url=None if ENV == "prod" else "/openapi.json")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]


class PredictRequest(BaseModel):
    instances: List[List[float]] = Field(..., min_length=1, max_length=MAX_BATCH)


class PredictResponse(BaseModel):
    probabilities: List[List[float]]
    model: str = "fraud-clf"
    version: str = MODEL_VERSION


@app.get("/api/health")
def health():
    return {"status": "ok", "model": "fraud-clf", "version": MODEL_VERSION, "features": FEATURES}


@app.post("/api/predict", response_model=PredictResponse)
@limiter.limit(RATE_LIMIT)
def predict(request: Request, req: PredictRequest):
    who = identity(request)
    for row in req.instances:
        if len(row) != model.n_features:
            REQUESTS.labels(who, "422").inc()
            raise HTTPException(422, f"each instance needs {model.n_features} features: {FEATURES}")
    try:
        probs = model.predict_proba(req.instances)
    except ValueError as e:
        REQUESTS.labels(who, "422").inc()
        raise HTTPException(422, str(e)) from e
    REQUESTS.labels(who, "200").inc()
    return PredictResponse(probabilities=probs.round(6).tolist())


@app.get("/metrics")
def metrics():
    """Prometheus scrape target — per-identity counters feed the extraction alert (Lab 12.2)."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
