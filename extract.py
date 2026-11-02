#!/usr/bin/env python3
"""Lab 12.2 — model extraction: build a surrogate from endpoint queries only, report fidelity."""
import sys

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from live_client import predict

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
X_test = np.load("data/X_probe.npy")
rng = np.random.default_rng(0)
lo, hi = X_test.min(0), X_test.max(0)
X_probe = rng.uniform(lo, hi, size=(N, X_test.shape[1]))     # attacker needs no real data, only ranges
y_stolen = predict(X_probe).argmax(1)
surrogate = RandomForestClassifier(n_estimators=200, random_state=0).fit(X_probe, y_stolen)
fidelity = accuracy_score(predict(X_test).argmax(1), surrogate.predict(X_test))
print(f"queries={N} surrogate_fidelity={fidelity:.3f}")
