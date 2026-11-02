#!/usr/bin/env python3
"""Write data/reference_stats.json from the CLEAN training data: the statistics later gates compare against
(exercise 6's drift check, exercise 37's per-decile fraud rate, exercise 44's PSI buckets). Run once after clean.py; commit the file."""
import json, sys, pandas as pd, numpy as np
src = sys.argv[1] if len(sys.argv) > 1 else "data/clean/train.csv"
df = pd.read_csv(src)
stats = {
    "rows": int(len(df)), "fraud_rate": float(df.label.mean()),
    "fraud_amount_mean": float(df[df.label == 1].amount.mean()), "legit_amount_mean": float(df[df.label == 0].amount.mean()),
    "fraud_rate_by_merchant_risk_decile": [float(x) for x in df.groupby(pd.qcut(df.merchant_risk, 10, labels=False, duplicates="drop")).label.mean()],
    "feature_buckets": {c: [float(x) for x in np.quantile(df[c], np.linspace(0, 1, 11))] for c in ["amount", "hour", "merchant_risk", "velocity_24h"]},
}
json.dump(stats, open("data/reference_stats.json", "w"), indent=1); print("wrote data/reference_stats.json:", {k: stats[k] for k in ("rows", "fraud_rate")})
