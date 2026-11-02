# fraud-clf — the SecMLOps course project (reference solution)

A deliberately small, fully working ML application: synthetic card-transaction data → a fraud
classifier → a FastAPI inference service → test and production Kubernetes environments.
This is the **finished state** of the course project. Students start from `secmlops-project-baseline`
and reach this by completing the labs on their chosen track (GitHub Actions, GitLab CI, or Azure DevOps).

## Branch strategy (all three tracks)

    feature/*, hotfix/*  --PR-->  main  --auto-->  TEST  --approval-->  PRODUCTION

- **PR to main**: data gate · code gates · train + robustness gates · build + image gate. Nothing deploys;
  required checks block the merge until green.
- **Push to main**: register (ModelScan, sign, MLflow, evidence-gated Staging) → release (push by digest,
  Cosign sign, attest SBOM/ML-BOM/provenance) → **test** (Kyverno admission, rollout, smoke) → validate test
  (recon, TLS, authenticated DAST, live model attacks) → report to SecObserve → `promote_check` (0 open
  criticals) → **production** behind approval. The same digest moves through both environments.
- **Nightly**: test-environment validation only.

| Track | Entry point | Environments | Approval |
|---|---|---|---|
| GitHub Actions | `.github/workflows/pipeline.yml` | `test`, `production` | environment required reviewers |
| GitLab CI | `.gitlab-ci.yml` | `test`, `production` | protected environment + manual job |
| Azure DevOps | `azure-pipelines.yml` | `test`, `production` | environment approval check |

## What's here → which lab

| Path | Purpose | Lab |
|---|---|---|
| `gen_data.py` (`--poison`), `clean.py`, `validate.py`, `dvc.yaml` | deterministic data; Pandera gate | 3.1 |
| `train.py` → `scratch/candidate.joblib` + `model/model.safetensors` | training; weights-only export | 5.1, 6.1 |
| `art_gate.py`, `giskard_gate.py`, `tools/weak_candidate.py` | robustness gates (eps 0.5 / 0.80); the failing case | 5.1 |
| `src/fraudclf/model.py` | safetensors export; pure-numpy inference, **no pickle** | 6.1 |
| `register.py`, `promote_model.py` | MLflow lineage triple; evidence-gated promotion | 6.1, 6.2 |
| `mlbom.py` | CycloneDX ML-BOM with dataset components | 7.1, 7.2 |
| `Dockerfile`, `requirements-serve.txt` | pinned-digest, multi-stage, distroless, non-root | 7.1 |
| `src/serve.py` | **verifies checksum + signature before load (fail closed)**; 422 on bad input; per-identity 429; `/metrics` | 6.1, 9.1, 12 |
| `k8s/serve.yaml` | digest-pinned, non-root, Kyverno-admissible | 9.1 |
| `tests/` | smoke, safetensors≡sklearn, tampered-model refusal, 429 budget | 6.1, 9.1, 12.2, 14.1 |
| `live_*.py`, `extract.py`, `to_sarif.py`, `rapidast.yaml` | black-box attacks; normalization; authenticated DAST | 11–13 |
| `ci/` | shared stage scripts every platform wraps | all |

## Is my machine ready?

    scripts/ready-check.sh        # Windows: run from Git Bash

## Run it locally (no lab)

    pip install -r requirements.txt && export PYTHONPATH=. DISABLE_PANDERA_IMPORT_WARNING=True
    python gen_data.py && python clean.py && python validate.py     # DATA-GATE-PASS
    python train.py                                                  # clean accuracy: 0.988
    python art_gate.py                                               # adversarial=0.865 → exit 0
    pytest -q                                                        # 9 passed
    python tools/weak_candidate.py && python art_gate.py             # adversarial=0.492 → exit 1
    python train.py                                                  # restore
    python gen_data.py --poison --out /tmp/p.csv && python validate.py /tmp/p.csv   # exit 1
    VERIFY_MODEL=false uvicorn src.serve:app --port 8080

## API contract

    POST /api/predict {"instances": [[amount, hour, merchant_risk, velocity_24h], ...]}
    -> {"probabilities": [[p_legit, p_fraud], ...], "model": "fraud-clf", "version": "<git sha>"}
    GET /api/health · GET /metrics

Oversized (>256) / malformed / wrong-shape → 422, never 500. Per-identity budget (`X-Pomerium-Claim-Email`,
default 200/hour) → 429. `ENV=prod` disables `/docs` and `/openapi.json`.

## Secrets

None in this repo or in pipeline variables. Every stage authenticates to OpenBao through the platform's
workload identity and reads what it needs at runtime.
