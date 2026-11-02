"""Smoke tests (Lab 9.1 post-deploy). Run against a live URL via API_URL, or in-process."""
import os

import pytest

API = os.environ.get("API_URL")


@pytest.fixture(scope="module")
def client():
    if API:
        import httpx
        return httpx.Client(base_url=API, verify=os.environ.get("API_VERIFY_TLS", "false") == "true", timeout=15)  # noqa: S501
    os.environ["VERIFY_MODEL"] = "false"
    from fastapi.testclient import TestClient

    from src.serve import app
    return TestClient(app)


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["model"] == "fraud-clf"


def test_predict_ok(client):
    r = client.post("/api/predict", json={"instances": [[120.0, 14, 0.2, 1], [4800.0, 3, 0.9, 7]]})
    assert r.status_code == 200
    p = r.json()["probabilities"]
    assert len(p) == 2 and abs(sum(p[0]) - 1) < 1e-4
    assert p[1][1] > p[0][1]   # night-time, high-risk, high-velocity looks more fraudulent


def test_wrong_shape_422(client):
    assert client.post("/api/predict", json={"instances": [[1, 2, 3]]}).status_code == 422


def test_malformed_422(client):
    assert client.post("/api/predict", json={"instances": "nope"}).status_code == 422


def test_oversized_batch_422(client):
    assert client.post("/api/predict", json={"instances": [[1, 1, 0.1, 1]] * 5000}).status_code == 422


def test_rate_limit_is_429(client):
    """Per-identity budget (Lab 12.2). In-process only, where RATE_LIMIT is controllable."""
    if API:
        pytest.skip("rate-limit test runs in-process")
    from src import serve
    serve.limiter.reset()
    limited = serve.limiter.limit("3/minute")(serve.predict)
    serve.app.router.routes = [r for r in serve.app.router.routes if getattr(r, "path", "") != "/api/predict"]
    serve.app.add_api_route("/api/predict", limited, methods=["POST"], response_model=serve.PredictResponse)
    hdr = {"x-pomerium-claim-email": "attacker@example.com"}
    body = {"instances": [[120.0, 14, 0.2, 1]]}
    codes = [client.post("/api/predict", json=body, headers=hdr).status_code for _ in range(5)]
    assert codes[:3] == [200, 200, 200] and 429 in codes[3:]


def test_metrics_endpoint(client):
    r = client.get("/metrics")
    assert r.status_code == 200 and b"inference_requests_total" in r.content
