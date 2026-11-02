#!/usr/bin/env bash
# Stage: validate-staging. Recon + TLS + DAST + live model attacks (ch. 11-12).
set -uo pipefail   # not -e: collect all findings, gate later
source "$(dirname "$0")/versions.env"
TARGET="${STAGING:-https://staging.secmlops.com}"
nmap -sV -oX nmap.xml "${TARGET#https://}" || true
katana -u "$TARGET" -jc -o urls.txt || true
nuclei -l urls.txt -severity medium,high,critical -sarif-export nuclei.sarif || true
./testssl.sh --jsonfile testssl.json "$TARGET" || true
./ci/rapidast.sh || true
python live_art.py || echo "ART gate flagged"
python live_giskard.py || true
echo "VALIDATE-STAGING-DONE"
