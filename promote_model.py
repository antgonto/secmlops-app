#!/usr/bin/env python3
"""Lab 6.2 — refuse a stage transition unless all evidence tags are present and green.
usage: promote_model.py <name> <version|latest> <Staging|Production>"""
import os
import sys

import mlflow

mlflow.set_tracking_uri(os.environ.get("MLFLOW", "http://mlflow.secmlops.com:5000"))
REQUIRED = {"modelscan": "passed", "art": "passed", "giskard": "passed"}
MUST_EXIST = ["git_sha", "dvc_lock", "signature"]
name, version, stage = sys.argv[1], sys.argv[2], sys.argv[3]
c = mlflow.MlflowClient()
if version == "latest":
    version = str(max(int(v.version) for v in c.search_model_versions(f"name='{name}'")))
mv = c.get_model_version(name, version)
missing = [k for k, w in REQUIRED.items() if mv.tags.get(k) != w] + [k for k in MUST_EXIST if k not in mv.tags]
if missing:
    print(f"BLOCKED: {name} v{version} -> {stage}; missing/failed evidence: {missing}")
    sys.exit(1)
c.transition_model_version_stage(name, version, stage=stage)
print(f"PROMOTED: {name} v{version} -> {stage}")
