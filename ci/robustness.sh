#!/usr/bin/env bash
# Stage: robustness. ART + Giskard gates before registration (lesson 5.1).
set -euo pipefail
python art_gate.py
python giskard_gate.py
echo "ROBUSTNESS-GATES-PASS"
