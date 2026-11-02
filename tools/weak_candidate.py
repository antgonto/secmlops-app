#!/usr/bin/env python3
"""Lab 5.1 Part 4 — a candidate that LOOKS good (clean ~0.97) but FAILS the ART gate (adv ~0.49).

Over-weighting the fraud class pushes the decision boundary into the legitimate-class mass, so small
perturbations flip many decisions. A realistic mistake, not an artificial one.
Writes scratch/candidate.joblib and model/model.safetensors (overwrites the good one; re-run train.py to restore).
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.fraudclf.model import FEATURES, export_safetensors

df = pd.read_csv("data/clean/train.csv")
pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight={0: 1, 1: 30}))
pipe.fit(df[FEATURES].values.astype(np.float32), df["label"].values)
joblib.dump(pipe, "scratch/candidate.joblib")
export_safetensors(pipe, "model/model.safetensors")
print("weak candidate written (class_weight 1:30) — run art_gate.py to see it fail")
