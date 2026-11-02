"""Lab 12.1 — black-box access to the deployed endpoint. Uses only the public API."""
import os

import numpy as np
import requests

TOKEN = os.environ["STAGING_TOKEN"]
URL = os.environ.get("STAGING", "https://staging.secmlops.com") + "/api/predict"
VERIFY = os.environ.get("API_VERIFY_TLS", "false") == "true"


def predict(x: np.ndarray) -> np.ndarray:
    out = []
    for i in range(0, len(x), 200):
        r = requests.post(URL, headers={"Authorization": f"Bearer {TOKEN}"},
                          json={"instances": np.asarray(x[i:i + 200]).tolist()}, timeout=30, verify=VERIFY)  # noqa: S501
        r.raise_for_status()
        out.extend(r.json()["probabilities"])
    return np.array(out)
