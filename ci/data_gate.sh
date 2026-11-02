#!/usr/bin/env bash
# Stage: data. DVC integrity + Pandera validation (lesson 3.1).
set -euo pipefail
source "$(dirname "$0")/versions.env"
echo "== DVC integrity =="
dvc pull
dvc status -c
echo "== Pandera validation =="
python validate.py
echo "DATA-GATE-PASS"
