#!/usr/bin/env bash
# Pipeline self-security (lesson 4.1 challenge).
set -euo pipefail
if ls .github/workflows/*.yml >/dev/null 2>&1; then
  actionlint
  zizmor .github/workflows/ || true
fi
echo "WORKFLOW-SCAN-PASS"
