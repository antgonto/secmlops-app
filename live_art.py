#!/usr/bin/env python3
"""Lab 12.1 — black-box HopSkipJump against the live endpoint; re-enforce the threshold at test."""
import sys

import numpy as np
from art.attacks.evasion import HopSkipJump
from art.estimators.classification import BlackBoxClassifier

from live_client import predict

THRESHOLD = 0.80
X, y = np.load("data/X_probe.npy")[:120], np.load("data/y_probe.npy")[:120]
clf = BlackBoxClassifier(predict, input_shape=X.shape[1:], nb_classes=2)
clean = (clf.predict(X).argmax(1) == y).mean()
X_adv = HopSkipJump(clf, max_iter=8, max_eval=300, init_eval=30, verbose=False).generate(X)
adv = (clf.predict(X_adv).argmax(1) == y).mean()
print(f"live clean={clean:.3f} adversarial={adv:.3f} threshold={THRESHOLD}")
sys.exit(0 if adv >= THRESHOLD else 1)
