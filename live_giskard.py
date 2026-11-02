#!/usr/bin/env python3
"""Lab 12.1 — Giskard scan of the deployed endpoint's behavior."""
import sys

import giskard
import pandas as pd

from live_client import predict
from src.fraudclf.model import FEATURES

df = pd.read_csv("data/clean/train.csv").head(300)
model = giskard.Model(lambda d: predict(d[FEATURES].values.astype(float)), model_type="classification",
                      classification_labels=[0, 1], feature_names=FEATURES)
report = giskard.scan(model, giskard.Dataset(df, target="label"))
report.to_html("giskard-live.html")
majors = [i for i in report.issues if i.level == "major"]
print(f"live giskard: {len(report.issues)} issues, {len(majors)} major")
sys.exit(1 if majors else 0)
