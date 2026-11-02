"""Weights-only model I/O.

Training uses scikit-learn; serving must not unpickle anything. The StandardScaler +
LogisticRegression parameters are exported to safetensors and the forward pass is
re-implemented in numpy. Serving depends only on numpy + safetensors.
"""
from typing import Sequence, Union

import numpy as np
from safetensors.numpy import load_file, save_file

ArrayLike = Union[np.ndarray, Sequence[Sequence[float]]]
FEATURES = ["amount", "hour", "merchant_risk", "velocity_24h"]


def export_safetensors(sk_pipeline, path: str) -> None:
    scaler = sk_pipeline.named_steps["standardscaler"]
    lr = sk_pipeline.named_steps["logisticregression"]
    save_file(
        {
            "scaler_mean": scaler.mean_.astype(np.float32),
            "scaler_scale": scaler.scale_.astype(np.float32),
            "coef": lr.coef_.astype(np.float32),
            "intercept": lr.intercept_.astype(np.float32),
        },
        path,
        metadata={"model": "fraud-clf", "features": ",".join(FEATURES), "format": "logreg-v1"},
    )


class FraudModel:
    """Pure-numpy logistic regression loaded from safetensors."""

    def __init__(self, path: str):
        w = load_file(path)
        self.mean, self.scale = w["scaler_mean"], w["scaler_scale"]
        self.coef, self.intercept = w["coef"], w["intercept"]
        self.n_features = self.coef.shape[1]

    def predict_proba(self, X: ArrayLike) -> np.ndarray:
        X = np.asarray(X, dtype=np.float32)
        if X.ndim != 2 or X.shape[1] != self.n_features:
            raise ValueError(f"expected shape (n, {self.n_features}), got {X.shape}")
        z = ((X - self.mean) / self.scale) @ self.coef.T + self.intercept
        p1 = 1.0 / (1.0 + np.exp(-z))
        return np.hstack([1.0 - p1, p1])

    def predict(self, X: ArrayLike) -> np.ndarray:
        return self.predict_proba(X).argmax(axis=1)
