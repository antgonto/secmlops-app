#!/usr/bin/env python3
"""Train the fraud classifier.

Outputs
  scratch/candidate.joblib   sklearn model for the pre-registration gates (never shipped)
  model/model.safetensors    weights-only artifact for serving (the only thing in model/)
  data/X_test.npy, data/y_test.npy, data/X_probe.npy, data/y_probe.npy
"""
import json
import pathlib

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.fraudclf.model import FEATURES, export_safetensors

df = pd.read_csv("data/clean/train.csv")
X, y = df[FEATURES].values.astype(np.float32), df["label"].values
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0)).fit(X_tr, y_tr)
acc = clf.score(X_te, y_te)

pathlib.Path("scratch").mkdir(exist_ok=True)
pathlib.Path("model").mkdir(exist_ok=True)
joblib.dump(clf, "scratch/candidate.joblib")
export_safetensors(clf, "model/model.safetensors")
np.save("data/X_test.npy", X_te)
np.save("data/y_test.npy", y_te)
probe = min(400, len(X_te))
np.save("data/X_probe.npy", X_te[:probe])
np.save("data/y_probe.npy", y_te[:probe])
json.dump({"clean_accuracy": round(float(acc), 4), "features": FEATURES, "n_train": int(len(X_tr))},
          open("model/metrics.json", "w"), indent=2)
print(f"clean accuracy: {acc:.3f}  -> model/model.safetensors")
