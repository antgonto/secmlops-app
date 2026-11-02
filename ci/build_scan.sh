#!/usr/bin/env bash
# Stage: build. Image build + Trivy gate + SBOM + ML-BOM (lesson 7.1).
set -euo pipefail
source "$(dirname "$0")/versions.env"
docker build -t "$IMAGE:$GIT_SHA" .
trivy image --severity CRITICAL,HIGH --exit-code 1 -f json -o trivy.json "$IMAGE:$GIT_SHA"
trivy image --format cyclonedx -o sbom.cdx.json "$IMAGE:$GIT_SHA"
python mlbom.py
echo "BUILD-SCAN-PASS"
