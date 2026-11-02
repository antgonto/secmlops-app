#!/usr/bin/env python3
"""Lab 5.1 — ART evasion gate. Exit 1 if adversarial accuracy < THRESHOLD (calibrated: eps 0.5, 0.80)."""
import sys

import joblib
import numpy as np
from art.attacks.evasion import FastGradientMethod
from art.estimators.classification import SklearnClassifier

THRESHOLD, EPS = 0.80, 0.50
X, y = np.load("data/X_test.npy"), np.load("data/y_test.npy")
pipe = joblib.load("scratch/candidate.joblib")
scaler, lr = pipe.named_steps["standardscaler"], pipe.named_steps["logisticregression"]
Xs = scaler.transform(X).astype(np.float32)          # attack in scaled space: eps comparable across features
clf = SklearnClassifier(model=lr)
clean = (clf.predict(Xs).argmax(1) == y).mean()
Xs_adv = FastGradientMethod(clf, eps=EPS).generate(Xs)
adv = (clf.predict(Xs_adv).argmax(1) == y).mean()
print(f"clean={clean:.3f} adversarial={adv:.3f} eps={EPS} threshold={THRESHOLD}")
sys.exit(0 if adv >= THRESHOLD else 1)
