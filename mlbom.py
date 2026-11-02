#!/usr/bin/env python3
"""Labs 7.1/7.2 — CycloneDX ML-BOM: the model + every DVC-tracked dataset, with dependency edges."""
import datetime
import json
import os

import yaml

from src.fraudclf.gitmeta import git_sha, sha256_file

sha = git_sha(short=True)
SHA_FILE = "model/model.safetensors.sha256"
model_hash = open(SHA_FILE).read().split()[0] if os.path.exists(SHA_FILE) else sha256_file("model/model.safetensors")
lock_hash = sha256_file("dvc.lock") if os.path.exists("dvc.lock") else "n/a"

data_comps = []
if os.path.exists("dvc.lock"):
    for stage, body in yaml.safe_load(open("dvc.lock")).get("stages", {}).items():
        for out in body.get("outs", []):
            comp = {
                "type": "data",
                "bom-ref": "data:" + out["path"],
                "name": out["path"],
                "hashes": [{"alg": "MD5", "content": out["md5"]}],
                "properties": [{"name": "dvc.stage", "value": stage}],
            }
            if os.path.exists(out["path"]):
                comp["hashes"].append({"alg": "SHA-256", "content": sha256_file(out["path"])})
            data_comps.append(comp)

model_comp = {
    "type": "machine-learning-model",
    "bom-ref": "model:fraud-clf",
    "name": "fraud-clf",
    "version": sha,
    "hashes": [{"alg": "SHA-256", "content": model_hash}],
    "modelCard": {"properties": [
        {"name": "artifact.format", "value": "safetensors"},
        {"name": "robustness.art_eps", "value": "0.50"},
        {"name": "robustness.adv_accuracy_min", "value": "0.80"},
        {"name": "dataset.dvc_lock_sha256", "value": lock_hash},
    ]},
}
bom = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.6",
    "metadata": {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()},
    "components": [model_comp] + data_comps,
    "dependencies": [{"ref": "model:fraud-clf", "dependsOn": [c["bom-ref"] for c in data_comps]}],
}
json.dump(bom, open("mlbom.cdx.json", "w"), indent=2)
print(f"ML-BOM written: model + {len(data_comps)} dataset components")
