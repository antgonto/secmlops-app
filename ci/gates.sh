#!/usr/bin/env bash
# Stage: gates. Branch gate chain (lesson 4.1). Shared by all 3 platforms.
set -euo pipefail
source "$(dirname "$0")/versions.env"
echo "== quality =="
ruff check .
mypy src/
pytest -q
echo "== SAST (Opengrep) =="
# Opengrep: LGPL-2.1 community fork of Semgrep CE. Semgrep's own registry rules
# were relicensed (Dec 2024) for internal/non-SaaS use only, so we use the
# open Opengrep rules repo instead. Output file name kept as semgrep.json for
# SecObserve's parser compatibility (SARIF-compatible JSON).
[ -d /tmp/opengrep-rules ] || git clone --depth 1 https://github.com/opengrep/opengrep-rules /tmp/opengrep-rules
opengrep scan --config /tmp/opengrep-rules/python --error --json -o semgrep.json
echo "== SCA (Trivy fs) =="
trivy fs --scanners vuln --severity CRITICAL,HIGH --exit-code 1 -f json -o trivy-fs.json .
echo "== secrets (Gitleaks) =="
gitleaks detect --source . --log-opts="--all" -f json -r gitleaks.json
echo "GATES-PASS"
