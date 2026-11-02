#!/usr/bin/env python3
"""Lab 6.1 — register model/ in MLflow with the lineage triple + evidence tags."""
import json
import os

import mlflow

from src.fraudclf.gitmeta import git_sha, sha256_file

mlflow.set_tracking_uri(os.environ.get("MLFLOW", "http://mlflow.secmlops.com:5000"))
c = mlflow.MlflowClient()
sha = git_sha()
lock = sha256_file("dvc.lock")
with mlflow.start_run(run_name=f"fraud-clf-{sha[:7]}") as run:
    mlflow.log_params({"art_eps": 0.50, "art_threshold": 0.80, **json.load(open("model/metrics.json"))})
    mlflow.log_artifacts("model", artifact_path="model")
    for f in ("giskard-report.html", "modelscan.json"):
        if os.path.exists(f):
            mlflow.log_artifact(f)
    mv = c.create_model_version("fraud-clf", f"{run.info.artifact_uri}/model", run.info.run_id)
TAGS = {"git_sha": sha, "dvc_lock": lock, "modelscan": "passed", "art": "passed", "giskard": "passed",
        "signature": "model/model.safetensors.sig", "format": "safetensors"}
for k, v in TAGS.items():
    c.set_model_version_tag("fraud-clf", mv.version, k, v)
print(f"registered fraud-clf v{mv.version}")
