#!/usr/bin/env python3
"""Pandera data gate (Lab 3.1). Exit 1 on any schema or distribution violation."""
import sys

import pandas as pd
import pandera as pa
from pandera import Check, Column

schema = pa.DataFrameSchema(
    {
        "amount": Column(float, Check.in_range(0, 50_000)),
        "hour": Column(int, Check.in_range(0, 23)),
        "merchant_risk": Column(float, Check.in_range(0.0, 1.0)),
        "velocity_24h": Column(int, Check.ge(0)),
        "label": Column(int, Check.isin([0, 1])),
    },
    checks=[
        Check(lambda df: df.label.mean() < 0.40, error="class balance drifted (fraud rate >= 40%)"),
        Check(lambda df: len(df) >= 500, error="too few rows"),
    ],
    strict=True,
)

path = sys.argv[1] if len(sys.argv) > 1 else "data/clean/train.csv"
try:
    schema.validate(pd.read_csv(path), lazy=True)
    print("DATA-GATE-PASS")
except pa.errors.SchemaErrors as e:
    print(e.failure_cases.to_string())
    sys.exit(1)
