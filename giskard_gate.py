#!/usr/bin/env python3
"""Lab 5.1 — Giskard scan gate. Exit 1 on any major issue."""
import sys

import giskard
import joblib
import pandas as pd

from src.fraudclf.model import FEATURES

pipe = joblib.load("scratch/candidate.joblib")
df = pd.read_csv("data/clean/train.csv").sample(n=600, random_state=1)
model = giskard.Model(lambda d: pipe.predict_proba(d[FEATURES].values), model_type="classification",
                      classification_labels=[0, 1], feature_names=FEATURES)
report = giskard.scan(model, giskard.Dataset(df, target="label"))
report.to_html("giskard-report.html")
majors = [i for i in report.issues if i.level == "major"]
print(f"giskard issues: {len(report.issues)} total, {len(majors)} major")
sys.exit(1 if majors else 0)
