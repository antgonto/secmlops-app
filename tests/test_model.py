import joblib
import numpy as np

from src.fraudclf.model import FraudModel


def test_safetensors_matches_sklearn():
    pipe = joblib.load("scratch/candidate.joblib")
    m = FraudModel("model/model.safetensors")
    X = np.load("data/X_test.npy")[:50]
    assert np.allclose(pipe.predict_proba(X), m.predict_proba(X), atol=1e-5)
