#!/usr/bin/env bash
# Authenticated DAST through Pomerium with an Entra ID token (lesson 11.1).
set -euo pipefail
TOKEN="$(az account get-access-token --resource "${ENTRA_APP_ID}" --query accessToken -o tsv)"
docker run --rm -v "$PWD:/work" ghcr.io/rapidast/rapidast:latest \
  rapidast.py --config /work/rapidast.yaml --auth-token "$TOKEN"
