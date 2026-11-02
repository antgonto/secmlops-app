#!/usr/bin/env bash
# Stage: report. Push every scanner report to SecObserve (lesson 13.1).
set -euo pipefail
source "$(dirname "$0")/versions.env"
: "${SO_TOKEN:?set SO_TOKEN}" ; : "${SO_PRODUCT:?set SO_PRODUCT}"
upload () { [ -f "$2" ] || { echo "skip $2"; return 0; }
  curl -sf -X POST "$SO_URL/api/import/file_upload/" \
    -H "Authorization: APIToken $SO_TOKEN" \
    -F "product=$SO_PRODUCT" -F "parser_name=$1" -F "file=@$2" >/dev/null && echo "uploaded $2 ($1)"; }
upload "Trivy"     trivy-fs.json
upload "Trivy"     trivy.json
upload "Semgrep"   semgrep.json
upload "Gitleaks"  gitleaks.json
upload "OWASP_ZAP" rapidast/zap.json
upload "SARIF"     nuclei.sarif
echo "SO-UPLOAD-DONE"
